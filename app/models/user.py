from datetime import date, datetime, timezone
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from pydantic import EmailStr


class UserBase(SQLModel,):
    name: str
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = ""

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_banned: bool = Field(default=False)
    is_muted: bool = Field(default=False)
    muted_until: Optional[datetime] = Field(default=None)


class Experience(SQLModel, table=True):
    __tablename__ = "experience"

    id: Optional[int] = Field(default=None, primary_key=True)
    alumni_profile_id: int = Field(foreign_key="alumni_profile.id", index=True)
    title: str
    employer: str
    start_date: date
    end_date: Optional[date] = None


class AlumniProfile(SQLModel, table=True):
    __tablename__ = "alumni_profile"

    id: Optional[int] = Field(default=None, primary_key=True)
    # student-build:code-check begin
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)
    headline: str = ""
    bio: str = ""
    graduation_year: str = ""
    major: str = ""
    school: str = ""
    location: str = ""
    industry: str = ""
    help_offered: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # student-build:code-check end
    user: User = Relationship()
    experiences: list[Experience] = Relationship()


class Follow(SQLModel, table=True):
    __tablename__ = "follow"

    id: Optional[int] = Field(default=None, primary_key=True)
    # student-build:code-check begin
    follower_user_id: int = Field(foreign_key="user.id", index=True)
    followed_profile_id: int = Field(foreign_key="alumni_profile.id", index=True)
    followed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (UniqueConstraint("follower_user_id", "followed_profile_id", name="unique_follow"),)
    # student-build:code-check end


class Event(SQLModel, table=True):
    __tablename__ = "event"

    id: Optional[int] = Field(default=None, primary_key=True)
    # student-build:code-check begin
    title: str
    description: str
    event_date: datetime
    event_time: str
    event_format: str
    location: str
    organizer_profile_id: int = Field(foreign_key="alumni_profile.id", index=True)
    # student-build:code-check end


class EventAttendee(SQLModel, table=True):
    __tablename__ = "event_attendee"

    id: Optional[int] = Field(default=None, primary_key=True)
    # student-build:code-check begin
    event_id: int = Field(foreign_key="event.id", index=True)
    attendee_profile_id: int = Field(foreign_key="alumni_profile.id", index=True)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("event_id", "attendee_profile_id", name="uq_event_attendee_pair"),
    )
    # student-build:code-check end


class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"

    id: Optional[int] = Field(default=None, primary_key=True)
    # student-build:code-check begin
    participant_one_user_id: int = Field(foreign_key="user.id", index=True)
    participant_two_user_id: int = Field(foreign_key="user.id", index=True)
    # student-build:code-check end


class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: Optional[int] = Field(default=None, primary_key=True)
    # student-build:code-check begin
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    sender_user_id: int = Field(foreign_key="user.id", index=True)
    recipient_user_id: int = Field(foreign_key="user.id", index=True)
    subject: str = ""
    body: str
    sent_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # student-build:code-check end


class Post(SQLModel, table=True):
    __tablename__ = "post"

    id: Optional[int] = Field(default=None, primary_key=True)
    # student-build:code-check begin
    author_profile_id: int = Field(foreign_key="alumni_profile.id", index=True)
    body: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # student-build:code-check end
    author_profile: AlumniProfile = Relationship()


class Report(SQLModel, table=True):
    __tablename__ = "report"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id", index=True)
    reporter_user_id: int = Field(foreign_key="user.id", index=True)
    reason: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("post_id", "reporter_user_id", name="uq_report_post_reporter"),
    )

    post: Post = Relationship()
    reporter: User = Relationship()