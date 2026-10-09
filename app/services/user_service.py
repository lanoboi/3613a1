from app.repositories.user import UserRepository
from app.models.user import AlumniProfile
from app.utilities.security import encrypt_password, verify_password, create_access_token
from app.schemas.user import RegularUserCreate
from typing import Optional

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_all_users(self):
        return self.user_repo.get_all_users()

    def get_alumni_profile_by_id(self, profile_id: int):
        # student-build:code-check begin
        return self.user_repo.get_alumni_profile_by_id(profile_id)
        # student-build:code-check end

    def get_alumni_profile_by_user_id(self, user_id: int):
        return self.user_repo.get_alumni_profile_by_user_id(user_id)

    def save_alumni_profile(self, user_id: int, profile_data: dict[str, str]):
        required_fields = ("school", "graduation_year", "major")
        if any(not profile_data.get(field_name, "").strip() for field_name in required_fields):
            raise ValueError("School, graduation year, and degree are required")

        profile = self.user_repo.get_alumni_profile_by_user_id(user_id)
        if profile is None:
            profile = AlumniProfile(user_id=user_id)

        for field_name, value in profile_data.items():
            setattr(profile, field_name, value.strip())

        return self.user_repo.save_alumni_profile(profile)

    def search_alumni_profiles(self, query: str = ""):
        return self.user_repo.search_alumni_profiles(query)

    def is_following(self, follower_user_id: int, followed_profile_id: int) -> bool:
        return self.user_repo.is_following(follower_user_id, followed_profile_id)

    def toggle_follow(self, follower_user_id: int, followed_profile_id: int) -> bool:
        return self.user_repo.toggle_follow(follower_user_id, followed_profile_id)
    