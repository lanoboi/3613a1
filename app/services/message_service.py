from app.repositories.message import MessageRepository


class MessageService:
    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    def get_inbox(self, user_id: int, conversation_id: int | None = None):
        return self.message_repo.get_inbox(user_id, conversation_id)

    def get_conversation(self, user_id: int, conversation_id: int):
        return self.message_repo.get_conversation(user_id, conversation_id)

    def get_profile_for_user(self, profile_id: int):
        return self.message_repo.get_profile_for_user(profile_id)

    def get_available_profiles(self, user_id: int):
        return self.message_repo.get_available_profiles(user_id)

    def send_to_profile(self, sender_user_id: int, profile_id: int, body: str):
        return self.message_repo.send_to_profile(sender_user_id, profile_id, body)

    def reply_to_conversation(self, sender_user_id: int, conversation_id: int, body: str):
        return self.message_repo.reply_to_conversation(
            sender_user_id, conversation_id, body
        )