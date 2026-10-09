from app.repositories.post import PostRepository
from app.models.user import Post
from datetime import datetime, timezone


class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def get_feed_for_user(self, user_id: int):
        return self.post_repo.get_feed_for_user(user_id)

    def get_profile_for_user(self, user_id: int):
        return self.post_repo.get_profile_for_user(user_id)

    def create_for_user(self, user_id: int, body: str):
        clean_body = body.strip()
        if not clean_body:
            raise ValueError("Post text cannot be empty")
        profile = self.post_repo.get_profile_for_user(user_id)
        if profile is None:
            raise ValueError("An alumni profile is required to publish")
        return self.post_repo.create(
            Post(
                author_profile_id=profile.id,
                body=clean_body,
                created_at=datetime.now(timezone.utc),
            )
        )