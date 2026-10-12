from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep, IsUserLoggedIn, get_current_user, is_admin
from app.repositories.moderation import ModerationRepository
from app.services.moderation_service import ModerationService

try:
    from app.utilities.flash import flash  # flash is defined in a module
except ImportError:
    from app.utilities import flash  # flash is exported by the package

from . import router, templates


def _moderation_service(db: SessionDep) -> ModerationService:
    return ModerationService(ModerationRepository(db))


def _redirect_to_admin() -> RedirectResponse:
    return RedirectResponse(
        url="/admin",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_home_view(
    request: Request,
    user: AdminDep,
    db:SessionDep
):
    moderation_service = _moderation_service(db)
    reports = moderation_service.list_reports()
    members = []
    for member in moderation_service.list_members():
        status_kind, status_label = ModerationService.member_status(member)
        members.append(
            {"member": member, "status_kind": status_kind, "status_label": status_label}
        )
    return templates.TemplateResponse(
        request=request, 
        name="admin.html",
        context={
            "user": user,
            "reports": reports,
            "members": members,
            "mute_options": [
                (preset, ModerationService.MUTE_LABELS[preset])
                for preset in ModerationService.MUTE_PRESETS
            ],
        }
    )


@router.post("/admin/reports/{report_id}/dismiss", name="admin_dismiss_report")
async def admin_dismiss_report(
    request: Request,
    report_id: int,
    user: AdminDep,
    db: SessionDep,
):
    moderation_service = _moderation_service(db)
    try:
        moderation_service.dismiss_report(report_id)
        flash(request, "Report dismissed.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    return _redirect_to_admin()


@router.post("/admin/posts/{post_id}/remove", name="admin_remove_post")
async def admin_remove_post(
    request: Request,
    post_id: int,
    user: AdminDep,
    db: SessionDep,
):
    moderation_service = _moderation_service(db)
    try:
        moderation_service.remove_post(post_id)
        flash(request, "Post removed.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    return _redirect_to_admin()


@router.post("/admin/users/{target_user_id}/ban", name="admin_ban_user")
async def admin_ban_user(
    request: Request,
    target_user_id: int,
    user: AdminDep,
    db: SessionDep,
):
    moderation_service = _moderation_service(db)
    try:
        moderation_service.ban_user(user, target_user_id)
        flash(request, "User banned. They can no longer sign in.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    return _redirect_to_admin()


@router.post("/admin/users/{target_user_id}/unban", name="admin_unban_user")
async def admin_unban_user(
    request: Request,
    target_user_id: int,
    user: AdminDep,
    db: SessionDep,
):
    moderation_service = _moderation_service(db)
    try:
        moderation_service.unban_user(user, target_user_id)
        flash(request, "User unbanned. They can sign in again.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    return _redirect_to_admin()


@router.post("/admin/users/{target_user_id}/mute", name="admin_mute_user")
async def admin_mute_user(
    request: Request,
    target_user_id: int,
    user: AdminDep,
    db: SessionDep,
    duration: str = Form(...),
):
    moderation_service = _moderation_service(db)
    label = ModerationService.MUTE_LABELS.get(duration, duration)
    try:
        moderation_service.mute_user(user, target_user_id, duration)
        if duration == "indefinite":
            flash(request, "User muted indefinitely. They can browse but not act.", "success")
        else:
            flash(request, f"User muted for {label}. They can browse but not act.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    return _redirect_to_admin()


@router.post("/admin/users/{target_user_id}/unmute", name="admin_unmute_user")
async def admin_unmute_user(
    request: Request,
    target_user_id: int,
    user: AdminDep,
    db: SessionDep,
):
    moderation_service = _moderation_service(db)
    try:
        moderation_service.unmute_user(user, target_user_id)
        flash(request, "User unmuted. They can act again.", "success")
    except ValueError as exc:
        flash(request, str(exc), "error")
    return _redirect_to_admin()
