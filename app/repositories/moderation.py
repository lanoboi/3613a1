from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.user import AlumniProfile, Post, Report, User


class ModerationRepository:
    """All SQL for content reports and account moderation."""

    def __init__(self, db: Session):
        self.db = db

    # --- reports -----------------------------------------------------------

    def create_report(self, report: Report) -> Report:
        try:
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception:
            self.db.rollback()
            raise

    def get_report(self, report_id: int) -> Report | None:
        return self.db.get(Report, report_id)

    def get_report_for_post_by_reporter(
        self, post_id: int, reporter_user_id: int
    ) -> Report | None:
        return self.db.exec(
            select(Report).where(
                Report.post_id == post_id,
                Report.reporter_user_id == reporter_user_id,
            )
        ).first()

    def list_reports(self) -> list[Report]:
        statement = (
            select(Report)
            .options(
                selectinload(Report.post)
                .selectinload(Post.author_profile)
                .selectinload(AlumniProfile.user),
                selectinload(Report.reporter),
            )
            .order_by(Report.created_at.desc(), Report.id.desc())
        )
        return self.db.exec(statement).all()

    def delete_report(self, report_id: int) -> None:
        report = self.db.get(Report, report_id)
        if report is None:
            return
        try:
            self.db.delete(report)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    # --- posts -------------------------------------------------------------

    def get_post(self, post_id: int) -> Post | None:
        return self.db.exec(
            select(Post)
            .options(selectinload(Post.author_profile).selectinload(AlumniProfile.user))
            .where(Post.id == post_id)
        ).first()

    def remove_post_with_reports(self, post_id: int) -> bool:
        """Delete a post and every report filed against it in one transaction."""
        post = self.db.get(Post, post_id)
        if post is None:
            return False
        reports = self.db.exec(
            select(Report).where(Report.post_id == post_id)
        ).all()
        try:
            for report in reports:
                self.db.delete(report)
            self.db.delete(post)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    # --- users -------------------------------------------------------------

    def list_users(self) -> list[User]:
        return self.db.exec(select(User).order_by(User.name)).all()

    def get_user(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def save_user(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise
