from sqlalchemy import or_
from sqlmodel import Session, select

from app.models.user import AlumniProfile, Follow, Post


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_feed_for_user(self, user_id: int):
        profile = self.get_profile_for_user(user_id)
        followed_profile_ids = select(Follow.followed_profile_id).where(
            Follow.follower_user_id == user_id
        )
        conditions = [Post.author_profile_id.in_(followed_profile_ids)]
        if profile is not None:
            conditions.append(Post.author_profile_id == profile.id)
        return self.db.exec(
            select(Post)
            .where(or_(*conditions))
            .order_by(Post.created_at.desc(), Post.id.desc())
        ).all()

    def get_profile_for_user(self, user_id: int):
        return self.db.exec(
            select(AlumniProfile).where(AlumniProfile.user_id == user_id)
        ).one_or_none()

    def get_by_author_and_body(
        self, author_profile_id: int, body: str
    ) -> Post | None:
        return self.db.exec(
            select(Post).where(
                Post.author_profile_id == author_profile_id,
                Post.body == body,
            )
        ).one_or_none()

    def create(self, post: Post) -> Post:
        self.db.add(post)
        try:
            self.db.commit()
            self.db.refresh(post)
            return post
        except Exception:
            self.db.rollback()
            raise