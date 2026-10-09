from sqlmodel import Session, select, func
from app.models.user import AlumniProfile, Follow, UserBase, User
from typing import Optional, Tuple
from app.utilities.pagination import Pagination
from app.schemas.user import UserUpdate
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: UserBase) -> Optional[User]:
        try:
            user_db = User.model_validate(user_data)
            self.db.add(user_db)
            self.db.commit()
            self.db.refresh(user_db)
            return user_db
        except Exception as e:
            logger.error(f"An error occurred while saving user: {e}")
            self.db.rollback()
            raise

    def search_users(self, query: str, page:int=1, limit:int=10) -> Tuple[list[User], Pagination]:
        offset = (page - 1) * limit
        db_qry = select(User)
        if query:
            db_qry = db_qry.where(
                User.username.ilike(f"%{query}%") | User.email.ilike(f"%{query}%")
            )
        count_qry = select(func.count()).select_from(db_qry.subquery())
        count_todos = self.db.exec(count_qry).one()

        users = self.db.exec(db_qry.offset(offset).limit(limit)).all()
        pagination = Pagination(total_count=count_todos, current_page=page, limit=limit)

        return users, pagination

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.exec(select(User).where(User.username == username)).one_or_none()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_alumni_profile_by_id(
        self, profile_id: int
    ) -> Optional[AlumniProfile]:
        # student-build:code-check begin
        return self.db.get(AlumniProfile, profile_id)
        # student-build:code-check end

    def get_alumni_profile_by_user_id(
        self, user_id: int
    ) -> Optional[AlumniProfile]:
        return self.db.exec(
            select(AlumniProfile).where(AlumniProfile.user_id == user_id)
        ).one_or_none()

    def save_alumni_profile(self, profile: AlumniProfile) -> AlumniProfile:
        try:
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except Exception:
            self.db.rollback()
            raise

    def search_alumni_profiles(self, query: str = "") -> list[AlumniProfile]:
        statement = select(AlumniProfile).join(User)
        if query.strip():
            term = f"%{query.strip()}%"
            statement = statement.where(
                User.name.ilike(term)
                | AlumniProfile.headline.ilike(term)
                | AlumniProfile.school.ilike(term)
                | AlumniProfile.industry.ilike(term)
            )
        return self.db.exec(statement.order_by(User.name)).all()

    def is_following(self, follower_user_id: int, followed_profile_id: int) -> bool:
        follow = self.db.exec(
            select(Follow).where(
                Follow.follower_user_id == follower_user_id,
                Follow.followed_profile_id == followed_profile_id,
            )
        ).first()
        return follow is not None

    def toggle_follow(self, follower_user_id: int, followed_profile_id: int) -> bool:
        if self.db.get(AlumniProfile, followed_profile_id) is None:
            raise ValueError("Alumni profile not found")

        try:
            existing = self.db.exec(
                select(Follow).where(
                    Follow.follower_user_id == follower_user_id,
                    Follow.followed_profile_id == followed_profile_id,
                )
            ).one_or_none()
            if existing is not None:
                self.db.delete(existing)
                self.db.commit()
                return False

            self.db.add(
                Follow(
                    follower_user_id=follower_user_id,
                    followed_profile_id=followed_profile_id,
                )
            )
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def get_all_users(self) -> list[User]:
        return self.db.exec(select(User)).all()

    def update_user(self, user_id:int, user_data: UserUpdate)->User:
        user = self.db.get(User, user_id)
        if not user:
            raise Exception("Invalid user id given")
        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"An error occurred while updating user: {e}")
            self.db.rollback()
            raise

    def delete_user(self, user_id: int):
        user = self.db.get(User, user_id)
        if not user:
            raise Exception("User doesn't exist")
        try:
            self.db.delete(user)
            self.db.commit()
        except Exception as e:
            logger.error(f"An error occurred while deleting user: {e}")
            self.db.rollback()
            raise
