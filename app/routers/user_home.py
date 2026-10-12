from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from app.repositories.moderation import ModerationRepository
from app.repositories.post import PostRepository
from app.services.moderation_service import ModerationService
from app.services.post_service import PostService

try:
    from app.utilities.flash import flash  # flash is defined in a module
except ImportError:
    from app.utilities import flash  # flash is exported by the package

from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    post_service = PostService(PostRepository(db))
    posts = post_service.get_feed_for_user(user.id)
    can_post = post_service.get_profile_for_user(user.id) is not None
    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={
            "user": user,
            "posts": posts,
            "can_post": can_post,
            "mute_message": ModerationService.mute_message(user),
        },
    )


@router.post("/posts", name="create_post")
async def create_post(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    body: str = Form(),
):
    # Muted users may browse but not act; block before the original snippet.
    mute_block = ModerationService.mute_message(user)
    if mute_block:
        flash(request, mute_block, "error")
        return RedirectResponse(
            url="/app",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    # student-build:code-check begin
    post_service = PostService(PostRepository(db))
    try:
        post_service.create_for_user(user.id, body)
        flash(request, "Post published.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    except Exception:
        flash(request, "Could not publish post.", "error")
    return RedirectResponse(
        url="/app",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    # student-build:code-check end


@router.post("/posts/{post_id}/report", name="report_post")
async def report_post(
    request: Request,
    post_id: int,
    user: AuthDep,
    db: SessionDep,
    reason: str = Form(""),
):
    moderation_service = ModerationService(ModerationRepository(db))
    try:
        moderation_service.require_can_act(user)
        moderation_service.report_post(user, post_id, reason)
        flash(request, "Thanks — your report was sent to the moderators.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    except Exception:
        flash(request, "Could not send the report.", "error")
    return RedirectResponse(
        url="/app",
        status_code=status.HTTP_303_SEE_OTHER,
    )
