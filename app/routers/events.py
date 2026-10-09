from fastapi import Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.event import EventRepository
from app.services.event_service import EventService
from app.utilities.flash import flash
from . import router, templates


@router.get("/events", response_class=HTMLResponse, name="events_view")
async def events_view(request: Request, user: AuthDep, db: SessionDep):
    event_service = EventService(EventRepository(db))
    upcoming_events, joined_events, can_join = event_service.get_event_sections(user.id)
    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={
            "user": user,
            "upcoming_events": upcoming_events,
            "joined_events": joined_events,
            "can_join": can_join,
        },
    )


@router.post("/events/{event_id}/attendance", name="toggle_event_attendance")
async def toggle_event_attendance(
    request: Request,
    event_id: int,
    user: AuthDep,
    db: SessionDep,
):
    # student-build:code-check begin
    event_service = EventService(EventRepository(db))
    try:
        is_attending = event_service.toggle_attendance(user.id, event_id)
        if is_attending:
            flash(request, "You have joined the event!", "success")
        else:
            flash(request, "You have left the event.", "info")
    except ValueError as exc:
        flash(request, str(exc), "error")
    except Exception:
        flash(request, "Could not update event attendance.", "error")
    return RedirectResponse(
        url=request.url_for("events_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    # student-build:code-check end