import logging
import threading
import time
from contextlib import contextmanager

from sqlalchemy.exc import DBAPIError, OperationalError, ProgrammingError
from sqlmodel import SQLModel, Session, create_engine

from app.config import get_settings

logger = logging.getLogger(__name__)

_schema_lock = threading.Lock()


def sqlalchemy_uri(uri: str) -> str:
    """Accept Render's postgres:// URLs in the sync SQLAlchemy engine."""
    if uri.startswith("postgres://"):
        return "postgresql+psycopg2://" + uri[len("postgres://") :]
    if uri.startswith("postgresql://"):
        return "postgresql+psycopg2://" + uri[len("postgresql://") :]
    return uri


engine = create_engine(
    sqlalchemy_uri(get_settings().database_uri),
    echo=get_settings().env.lower()
    in ["dev", "development", "test", "testing", "staging"],
    pool_size=get_settings().db_pool_size,
    max_overflow=get_settings().db_additional_overflow,
    pool_timeout=get_settings().db_pool_timeout,
    pool_recycle=get_settings().db_pool_recycle,
)


def upgrade_schema() -> None:
    """Add columns introduced after a table was first created.

    ``create_all`` only creates missing tables; it never alters existing ones.
    This applies the additive moderation columns so existing local and Render
    databases keep their data. No-op when the columns already exist.
    """
    from sqlalchemy import inspect, text

    additions = {
        "user": {
            "is_banned": 'ALTER TABLE "user" ADD COLUMN is_banned BOOLEAN DEFAULT FALSE NOT NULL',
            "is_muted": 'ALTER TABLE "user" ADD COLUMN is_muted BOOLEAN DEFAULT FALSE NOT NULL',
            "muted_until": 'ALTER TABLE "user" ADD COLUMN muted_until TIMESTAMP',
        },
    }

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    for table, columns in additions.items():
        if table not in existing_tables:
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table)}
        for name, ddl in columns.items():
            if name in existing_columns:
                continue
            logger.info("Upgrading schema: adding %s.%s", table, name)
            with engine.begin() as connection:
                connection.execute(text(ddl))


def create_db_and_tables() -> None:
    # Ensure model modules are imported so tables are registered on metadata.
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    upgrade_schema()


def drop_all() -> None:
    SQLModel.metadata.drop_all(bind=engine)


def is_db_not_ready_error(exc: BaseException) -> bool:
    """True when Postgres is unreachable or the schema/tables are missing."""
    if isinstance(exc, OperationalError):
        return True
    if isinstance(exc, ProgrammingError):
        return True
    if isinstance(exc, DBAPIError) and getattr(exc, "connection_invalidated", False):
        return True

    text = str(exc).lower()
    markers = (
        "does not exist",
        "undefinedtable",
        "undefined table",
        "no such table",
        "relation ",
        "could not connect",
        "connection refused",
        "connection timed out",
        "server closed the connection",
        "the database system is starting up",
        "remaining connection slots",
        "too many connections",
        "ssl connection has been closed",
    )
    return any(m in text for m in markers)


def ensure_db_and_tables(
    *,
    retries: int = 8,
    delay_seconds: float = 2.0,
) -> None:
    """Create tables, retrying while the prod DB is still coming up."""
    last: BaseException | None = None
    for attempt in range(1, retries + 1):
        try:
            with _schema_lock:
                create_db_and_tables()
            if attempt > 1:
                logger.info("Database schema ready after %s attempt(s)", attempt)
            return
        except Exception as exc:  # noqa: BLE001 — first-boot resilience
            last = exc
            if not is_db_not_ready_error(exc) or attempt >= retries:
                raise
            logger.warning(
                "Database not ready (attempt %s/%s): %s",
                attempt,
                retries,
                exc,
            )
            time.sleep(delay_seconds * attempt)
    if last is not None:
        raise last


def recover_if_uninitialized(exc: BaseException) -> bool:
    """If *exc* looks like a missing schema, create tables and return True."""
    if not is_db_not_ready_error(exc):
        return False
    logger.warning("Uninitialized database detected; creating tables: %s", exc)
    ensure_db_and_tables()
    return True


def _session_generator():
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()


def get_session():
    yield from _session_generator()


@contextmanager
def get_cli_session():
    yield from _session_generator()
