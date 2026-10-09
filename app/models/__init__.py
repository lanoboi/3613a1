"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import AlumniProfile, Conversation, Event, EventAttendee, Experience, Follow, Message, Post, User

__all__ = ["User", "AlumniProfile", "Experience", "Follow", "Event", "EventAttendee", "Conversation", "Message", "Post"]
