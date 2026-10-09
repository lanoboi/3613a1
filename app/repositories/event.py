from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.user import AlumniProfile, Event, EventAttendee


class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_event_sections(self, user_id: int):
        profile = self.db.exec(
            select(AlumniProfile).where(AlumniProfile.user_id == user_id)
        ).one_or_none()
        joined_events = []
        joined_event_ids = set()

        if profile is not None:
            joined_events = self.db.exec(
                select(Event)
                .join(EventAttendee, EventAttendee.event_id == Event.id)
                .where(EventAttendee.attendee_profile_id == profile.id)
                .order_by(Event.event_date, Event.event_time)
            ).all()
            joined_event_ids = {
                event.id for event in joined_events if event.id is not None
            }

        upcoming_query = select(Event).where(
            Event.event_date >= datetime.now(timezone.utc)
        )
        if joined_event_ids:
            upcoming_query = upcoming_query.where(
                Event.id.not_in(joined_event_ids)
            )
        upcoming_events = self.db.exec(
            upcoming_query.order_by(Event.event_date, Event.event_time)
        ).all()
        return upcoming_events, joined_events, profile is not None

    def toggle_attendance(self, user_id: int, event_id: int) -> bool:
        profile = self.db.exec(
            select(AlumniProfile).where(AlumniProfile.user_id == user_id)
        ).one_or_none()
        if profile is None:
            raise ValueError("An alumni profile is required to join events")

        if self.db.get(Event, event_id) is None:
            raise ValueError("Event not found")

        try:
            existing = self.db.exec(
                select(EventAttendee).where(
                    EventAttendee.event_id == event_id,
                    EventAttendee.attendee_profile_id == profile.id,
                )
            ).one_or_none()
            if existing is not None:
                self.db.delete(existing)
                self.db.commit()
                return False

            self.db.add(
                EventAttendee(
                    event_id=event_id,
                    attendee_profile_id=profile.id,
                )
            )
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def get_by_title(self, title: str):
        return self.db.exec(select(Event).where(Event.title == title)).one_or_none()

    def create_event(self, event: Event) -> Event:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event