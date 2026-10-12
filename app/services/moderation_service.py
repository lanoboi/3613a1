from datetime import datetime, timedelta, timezone

from app.models.user import Report, User
from app.repositories.moderation import ModerationRepository


def _as_utc(value: datetime) -> datetime:
    """SQLite returns naive datetimes; treat them as the UTC we stored."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class ModerationService:
    """Rules for reporting content and moderating accounts."""

    MUTE_PRESETS = {
        "1h": timedelta(hours=1),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "indefinite": None,
    }

    MUTE_LABELS = {
        "1h": "1 hour",
        "24h": "24 hours",
        "7d": "7 days",
        "30d": "30 days",
        "indefinite": "Indefinite",
    }

    def __init__(self, repo: ModerationRepository):
        self.repo = repo

    # --- shared checks (used by other services/routes) ----------------------

    @staticmethod
    def is_muted(user: User) -> bool:
        """True when the user's mute is currently in effect (expiry honoured)."""
        if not user.is_muted:
            return False
        if user.muted_until is None:
            return True
        return _as_utc(user.muted_until) > datetime.now(timezone.utc)

    @staticmethod
    def mute_message(user: User) -> str | None:
        """Block message when the user is muted, otherwise None."""
        if not ModerationService.is_muted(user):
            return None
        if user.muted_until is None:
            return "You are muted indefinitely. You can browse, but not post, follow, join events, message, or report."
        until = _as_utc(user.muted_until)
        return (
            f"You are muted until {until.strftime('%b %d, %Y %I:%M %p')} UTC. "
            "You can browse, but not post, follow, join events, message, or report."
        )

    @classmethod
    def require_can_act(cls, user: User) -> None:
        """Raise ValueError when the user is currently muted."""
        message = cls.mute_message(user)
        if message:
            raise ValueError(message)

    # --- reporting -----------------------------------------------------------

    def report_post(self, reporter: User, post_id: int, reason: str = "") -> Report:
        post = self.repo.get_post(post_id)
        if post is None:
            raise ValueError("Post not found.")
        if post.author_profile.user_id == reporter.id:
            raise ValueError("You cannot report your own post.")
        if self.repo.get_report_for_post_by_reporter(post_id, reporter.id):
            raise ValueError("You have already reported this post.")
        clean_reason = reason.strip()
        if len(clean_reason) > 500:
            raise ValueError("Report reason must be 500 characters or fewer.")
        return self.repo.create_report(
            Report(
                post_id=post_id,
                reporter_user_id=reporter.id,
                reason=clean_reason,
                created_at=datetime.now(timezone.utc),
            )
        )

    def list_reports(self) -> list[Report]:
        return self.repo.list_reports()

    def dismiss_report(self, report_id: int) -> None:
        if self.repo.get_report(report_id) is None:
            raise ValueError("Report not found.")
        self.repo.delete_report(report_id)

    def remove_post(self, post_id: int) -> None:
        if not self.repo.remove_post_with_reports(post_id):
            raise ValueError("Post not found.")

    # --- account moderation --------------------------------------------------

    @staticmethod
    def _guard_target(actor: User, target: User) -> None:
        if actor.id == target.id:
            raise ValueError("You cannot moderate your own account.")
        if target.role == "admin":
            raise ValueError("Admin accounts cannot be banned or muted.")

    def _get_target(self, actor: User, user_id: int) -> User:
        target = self.repo.get_user(user_id)
        if target is None:
            raise ValueError("User not found.")
        self._guard_target(actor, target)
        return target

    def list_members(self) -> list[User]:
        return self.repo.list_users()

    @classmethod
    def member_status(cls, member: User) -> tuple[str, str]:
        """Return (css_kind, label) for a member's moderation status."""
        if member.is_banned:
            return "banned", "Banned"
        if cls.is_muted(member):
            if member.muted_until is None:
                return "muted", "Muted indefinitely"
            until = _as_utc(member.muted_until)
            return "muted", f"Muted until {until.strftime('%b %d, %Y · %I:%M %p')} UTC"
        if member.is_muted:
            # Flag set but the time limit has passed — mute has expired.
            return "active", "Active (mute expired)"
        return "active", "Active"

    def ban_user(self, actor: User, user_id: int) -> User:
        target = self._get_target(actor, user_id)
        if target.is_banned:
            raise ValueError("That user is already banned.")
        target.is_banned = True
        return self.repo.save_user(target)

    def unban_user(self, actor: User, user_id: int) -> User:
        target = self._get_target(actor, user_id)
        if not target.is_banned:
            raise ValueError("That user is not banned.")
        target.is_banned = False
        return self.repo.save_user(target)

    def mute_user(self, actor: User, user_id: int, preset: str) -> User:
        if preset not in self.MUTE_PRESETS:
            raise ValueError("Choose a valid mute duration.")
        target = self._get_target(actor, user_id)
        if self.is_muted(target):
            raise ValueError("That user is already muted.")
        duration = self.MUTE_PRESETS[preset]
        target.is_muted = True
        target.muted_until = (
            None if duration is None else datetime.now(timezone.utc) + duration
        )
        return self.repo.save_user(target)

    def unmute_user(self, actor: User, user_id: int) -> User:
        target = self._get_target(actor, user_id)
        if not target.is_muted:
            raise ValueError("That user is not muted.")
        target.is_muted = False
        target.muted_until = None
        return self.repo.save_user(target)
