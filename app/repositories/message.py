from datetime import datetime, timezone

from sqlalchemy import and_, or_
from sqlmodel import Session, select

from app.models.user import AlumniProfile, Conversation, Message, User


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_inbox(self, user_id: int, conversation_id: int | None = None):
        conversations = self.db.exec(
            select(Conversation)
            .where(
                or_(
                    Conversation.participant_one_user_id == user_id,
                    Conversation.participant_two_user_id == user_id,
                )
            )
        ).all()
        inbox_items = []
        for conversation in conversations:
            other_user_id = (
                conversation.participant_two_user_id
                if conversation.participant_one_user_id == user_id
                else conversation.participant_one_user_id
            )
            other_user = self.db.get(User, other_user_id)
            latest_message = self.db.exec(
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .order_by(Message.sent_at.desc(), Message.id.desc())
                .limit(1)
            ).first()
            inbox_items.append(
                {
                    "conversation": conversation,
                    "other_user": other_user,
                    "latest_message": latest_message,
                }
            )

        inbox_items.sort(
            key=lambda item: (
                item["latest_message"].sent_at
                if item["latest_message"] is not None
                else datetime.min.replace(tzinfo=timezone.utc)
            ),
            reverse=True,
        )
        selected_item = next(
            (
                item
                for item in inbox_items
                if item["conversation"].id == conversation_id
            ),
            inbox_items[0] if inbox_items and conversation_id is None else None,
        )
        messages = []
        if selected_item is not None:
            messages = self.db.exec(
                select(Message)
                .where(
                    Message.conversation_id
                    == selected_item["conversation"].id
                )
                .order_by(Message.sent_at, Message.id)
            ).all()
        return inbox_items, selected_item, messages

    def get_conversation(self, user_id: int, conversation_id: int):
        raise NotImplementedError

    def get_profile_for_user(self, profile_id: int):
        return self.db.get(AlumniProfile, profile_id)

    def get_available_profiles(self, user_id: int):
        return self.db.exec(
            select(AlumniProfile)
            .join(User)
            .where(AlumniProfile.user_id != user_id)
            .order_by(User.name)
        ).all()

    def send_to_profile(
        self, sender_user_id: int, profile_id: int, body: str
    ) -> int:
        profile = self.get_profile_for_user(profile_id)
        if profile is None:
            raise ValueError("Alumni profile not found")
        return self._send_to_user(sender_user_id, profile.user_id, body)

    def reply_to_conversation(
        self, sender_user_id: int, conversation_id: int, body: str
    ) -> int:
        conversation = self.db.get(Conversation, conversation_id)
        if conversation is None or sender_user_id not in {
            conversation.participant_one_user_id,
            conversation.participant_two_user_id,
        }:
            raise ValueError("Conversation not found")
        recipient_user_id = (
            conversation.participant_two_user_id
            if conversation.participant_one_user_id == sender_user_id
            else conversation.participant_one_user_id
        )
        return self._send_to_user(sender_user_id, recipient_user_id, body, conversation)

    def _send_to_user(
        self,
        sender_user_id: int,
        recipient_user_id: int,
        body: str,
        conversation: Conversation | None = None,
    ) -> int:
        cleaned_body = body.strip()
        if not cleaned_body:
            raise ValueError("Message cannot be empty")
        if sender_user_id == recipient_user_id:
            raise ValueError("You cannot message yourself")

        try:
            if conversation is None:
                conversation = self.db.exec(
                    select(Conversation).where(
                        or_(
                            and_(
                                Conversation.participant_one_user_id == sender_user_id,
                                Conversation.participant_two_user_id == recipient_user_id,
                            ),
                            and_(
                                Conversation.participant_one_user_id == recipient_user_id,
                                Conversation.participant_two_user_id == sender_user_id,
                            ),
                        )
                    )
                ).one_or_none()
            if conversation is None:
                conversation = Conversation(
                    participant_one_user_id=sender_user_id,
                    participant_two_user_id=recipient_user_id,
                )
                self.db.add(conversation)
                self.db.flush()

            message = Message(
                conversation_id=conversation.id,
                sender_user_id=sender_user_id,
                recipient_user_id=recipient_user_id,
                subject="",
                body=cleaned_body,
                sent_at=datetime.now(timezone.utc),
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(conversation)
            return conversation.id
        except Exception:
            self.db.rollback()
            raise