from fastapi import Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.message import MessageRepository
from app.services.message_service import MessageService
from app.services.moderation_service import ModerationService
from app.utilities.flash import flash
from . import router, templates


@router.get("/messages", response_class=HTMLResponse, name="messages_view")
async def messages_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    conversation_id: int | None = None,
):
    message_service = MessageService(MessageRepository(db))
    conversations, selected_conversation, messages = message_service.get_inbox(
        user.id, conversation_id
    )
    return templates.TemplateResponse(
        request=request,
        name="messages.html",
        context={
            "user": user,
            "conversations": conversations,
            "selected_conversation": selected_conversation,
            "messages": messages,
        },
    )


@router.get(
    "/profiles/{profile_id}/message",
    response_class=HTMLResponse,
    name="compose_message_view",
)
async def compose_message_view(
    request: Request,
    profile_id: int,
    user: AuthDep,
    db: SessionDep,
):
    message_service = MessageService(MessageRepository(db))
    recipient = message_service.get_profile_for_user(profile_id)
    if recipient is None:
        flash(request, "Alumni profile not found.", "error")
        return RedirectResponse(url="/profiles", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="message-compose.html",
        context={"user": user, "recipient": recipient},
    )


@router.get("/messages/new", response_class=HTMLResponse, name="new_message_view")
async def new_message_view(request: Request, user: AuthDep, db: SessionDep):
    message_service = MessageService(MessageRepository(db))
    recipients = message_service.get_available_profiles(user.id)
    return templates.TemplateResponse(
        request=request,
        name="message-new.html",
        context={"user": user, "recipients": recipients},
    )


@router.post("/messages/new", name="send_new_message")
async def send_new_message(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    profile_id: int = Form(),
    body: str = Form(),
):
    mute_block = ModerationService.mute_message(user)
    if mute_block:
        flash(request, mute_block, "error")
        return RedirectResponse(
            url=request.url_for("new_message_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    message_service = MessageService(MessageRepository(db))
    try:
        conversation_id = message_service.send_to_profile(
            user.id, profile_id, body
        )
    except ValueError as exc:
        flash(request, str(exc), "error")
        return RedirectResponse(
            url=request.url_for("new_message_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(
        url=f"{request.url_for('messages_view')}?conversation_id={conversation_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/profiles/{profile_id}/messages", name="send_message")
async def send_message(
    request: Request,
    profile_id: int,
    user: AuthDep,
    db: SessionDep,
    body: str = Form(),
):
    mute_block = ModerationService.mute_message(user)
    if mute_block:
        flash(request, mute_block, "error")
        return RedirectResponse(
            url=request.url_for("view_alumni_profile", profile_id=profile_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    # student-build:code-check begin
    
    message_service = MessageService(MessageRepository(db))
    try:
        conversation_id = message_service.send_to_profile(user.id, profile_id, body)
    except ValueError as exc:
        flash(request, str(exc), "error")
        return RedirectResponse(
            url=request.url_for("view_alumni_profile", profile_id=profile_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    redirect_url = f"{request.url_for('messages_view')}?conversation_id={conversation_id}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    
    # student-build:code-check end


@router.post("/messages/{conversation_id}", name="reply_to_conversation")
async def reply_to_conversation(
    request: Request,
    conversation_id: int,
    user: AuthDep,
    db: SessionDep,
    body: str = Form(),
):
    mute_block = ModerationService.mute_message(user)
    if mute_block:
        flash(request, mute_block, "error")
        return RedirectResponse(
            url=request.url_for("messages_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    message_service = MessageService(MessageRepository(db))
    try:
        updated_conversation_id = message_service.reply_to_conversation(
            user.id, conversation_id, body
        )
    except ValueError as exc:
        flash(request, str(exc), "error")
        return RedirectResponse(
            url=request.url_for("messages_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(
        url=f"{request.url_for('messages_view')}?conversation_id={updated_conversation_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )