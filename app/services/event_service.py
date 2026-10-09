from app.repositories.event import EventRepository


class EventService:
    def __init__(self, event_repo: EventRepository):
        self.event_repo = event_repo

    def get_event_sections(self, user_id: int):
        return self.event_repo.get_event_sections(user_id)

    def toggle_attendance(self, user_id: int, event_id: int) -> bool:
        return self.event_repo.toggle_attendance(user_id, event_id)

    def get_by_title(self, title: str):
        return self.event_repo.get_by_title(title)

    def create_event(self, event):
        return self.event_repo.create_event(event)