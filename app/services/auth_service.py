from app.repositories.user import UserRepository
from app.utilities.security import encrypt_password, verify_password, create_access_token
from app.schemas.user import RegularUserCreate
from typing import Optional

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Optional[str]:
        user = self.user_repo.get_by_username(username)
        if not user or not verify_password(plaintext_password=password, encrypted_password=user.password):
            return None
        if user.is_banned:
            raise ValueError("Your account has been banned. Contact an administrator.")
        access_token = create_access_token(data={"sub": f"{user.id}", "role": user.role})
        return access_token

    def register_user(self, name: str, username: str, email: str, password: str):
        # Explicit check first so the message is clear; the unique
        # constraints on username and email remain the backstop.
        clean_username = username.strip()
        clean_email = email.strip()
        if not clean_username:
            raise ValueError("Username is required.")
        if not clean_email:
            raise ValueError("Email is required.")
        if self.user_repo.username_or_email_exists(clean_username, clean_email):
            raise ValueError("Username or email already exists.")
        try:
            new_user = RegularUserCreate(
                name=name,
                username=clean_username, 
                email=clean_email, 
                password=encrypt_password(password)
            )
        except Exception as exc:
            raise ValueError("Please enter a valid email address.") from exc
        return self.user_repo.create(new_user)
