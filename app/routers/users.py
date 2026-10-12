from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form
from app.dependencies import SessionDep
from app.dependencies.auth import AuthDep
from . import api_router, router, templates
from app.services.user_service import UserService
from app.services.moderation_service import ModerationService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from app.schemas import UserResponse


# API endpoint for listing users
@api_router.get("/users", response_model=list[UserResponse])
async def list_users(request: Request, db: SessionDep):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return user_service.get_all_users()


@router.get("/profiles", response_class=HTMLResponse, name="alumni_directory_view")
async def alumni_directory_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    q: str = "",
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    profiles = user_service.search_alumni_profiles(q)
    return templates.TemplateResponse(
        request=request,
        name="alumni_directory.html",
        context={"user": user, "profiles": profiles, "query": q},
    )


@router.get("/profile", response_class=HTMLResponse, name="my_alumni_profile_view")
async def my_alumni_profile_view(request: Request, user: AuthDep, db: SessionDep):
    user_service = UserService(UserRepository(db))
    profile = user_service.get_alumni_profile_by_user_id(user.id)
    if profile is None:
        return RedirectResponse(
            url=request.url_for("alumni_profile_form_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    return templates.TemplateResponse(
        request,
        "alumni_profile.html",
        {
            "user": user,
            "profile": profile,
            "is_following": False,
            "own_profile": True,
        },
    )


@router.get("/profile/complete", response_class=HTMLResponse, name="alumni_profile_form_view")
async def alumni_profile_form_view(request: Request, user: AuthDep, db: SessionDep):
    profile = UserService(UserRepository(db)).get_alumni_profile_by_user_id(user.id)
    return templates.TemplateResponse(
        request=request,
        name="alumni-profile-form.html",
        context={"user": user, "profile": profile},
    )


@router.post("/profile/complete", name="save_alumni_profile")
async def save_alumni_profile(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    school: str = Form(),
    graduation_year: str = Form(),
    major: str = Form(),
    headline: str = Form(""),
    bio: str = Form(""),
    location: str = Form(""),
    industry: str = Form(""),
    help_offered: str = Form(""),
):
    profile_data = {
        "school": school,
        "graduation_year": graduation_year,
        "major": major,
        "headline": headline,
        "bio": bio,
        "location": location,
        "industry": industry,
        "help_offered": help_offered,
    }
    try:
        profile = UserService(UserRepository(db)).save_alumni_profile(
            user.id, profile_data
        )
    except ValueError as exc:
        flash(request, str(exc), "error")
        return RedirectResponse(
            url=request.url_for("alumni_profile_form_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    flash(request, "Your alumni profile is ready.", "success")
    return RedirectResponse(
        url=request.url_for("view_alumni_profile", profile_id=profile.id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/profiles/{profile_id}", response_class=HTMLResponse)
async def view_alumni_profile(
    request: Request,
    profile_id: int,
    user: AuthDep,
    db: SessionDep,
):
    # student-build:code-check begin
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    profile = user_service.get_alumni_profile_by_id(profile_id)
    if not profile:
        flash(request, "Alumni profile not found.", "error")
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    own_profile = profile.user_id == user.id
    is_following = False if own_profile else user_service.is_following(user.id, profile_id)
    return templates.TemplateResponse(
        request,
        "alumni_profile.html",
        {
            "user": user,
            "profile": profile,
            "is_following": is_following,
            "own_profile": own_profile,
        })
    # student-build:code-check end


@router.post("/profiles/{profile_id}/follow", name="toggle_alumni_follow")
async def toggle_alumni_follow(
    request: Request,
    profile_id: int,
    user: AuthDep,
    db: SessionDep,
):
    # Muted users may browse but not act; block before the original snippet.
    mute_block = ModerationService.mute_message(user)
    if mute_block:
        flash(request, mute_block, "error")
        return RedirectResponse(
            url=request.url_for("view_alumni_profile", profile_id=profile_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    # student-build:code-check begin
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    try:
        is_following = user_service.toggle_follow(user.id, profile_id)
    except ValueError as exc:
        flash(request, str(exc), "error")
    else:
        message = "You are now following this alum." if is_following else "You unfollowed this alum."
        flash(request, message, "success")
    return RedirectResponse(url=request.url_for("view_alumni_profile", profile_id=profile_id), status_code=status.HTTP_303_SEE_OTHER)

    # student-build:code-check end