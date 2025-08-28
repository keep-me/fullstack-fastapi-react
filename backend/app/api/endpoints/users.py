"""
User endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.api.deps import (
    CurrentSuperUser,
    CurrentUser,
    PaginationDep,
    UserServiceDep,
    ValidUUIDDep,
)
from app.models.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserUpdate,
)
from app.utils.notification import (
    send_delete_user_email,
    send_password_changed_email,
    send_welcome_email,
)
from app.utils.response import create_response

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    current_superuser: CurrentSuperUser,
    user_in: UserCreate,
    user_service: UserServiceDep,
) -> UserPublic:
    """
    Create a new user.
    """
    new_user = await user_service.create_user(user_in=user_in)
    user_public = UserPublic.model_validate(new_user)
    await send_welcome_email(user_public)
    return user_public


@router.get("/me", response_model=UserPublic)
async def get_user_me(current_user: CurrentUser) -> UserPublic:
    """
    Get current user information.
    """
    return UserPublic.model_validate(current_user)


@router.get("/my_id", response_model=UUID)
async def get_my_id(current_user: CurrentUser) -> UUID:
    """
    Get current user ID.
    """
    return current_user.id


@router.get("/", response_model=list[UserPublic])
async def get_active_users(
    current_superuser: CurrentSuperUser,
    pagination: PaginationDep,
    user_service: UserServiceDep,
) -> list[UserPublic]:
    """
    Get all active users.
    """
    return await user_service.get_users(skip=pagination.skip, limit=pagination.limit)


@router.patch("/me", response_model=UserPublic)
async def update_user_me(
    current_user: CurrentUser,
    user_in: UserUpdate,
    user_service: UserServiceDep,
) -> UserPublic:
    """
    Update current user's information.
    """
    return await user_service.update_user_me(current_user=current_user, user_in=user_in)


@router.patch("/me/password")
async def update_password_me(
    current_user: CurrentUser,
    body: UpdatePassword,
    user_service: UserServiceDep,
    request: Request,
) -> JSONResponse:
    """
    Update current user's password.
    """
    await user_service.update_password_me(
        current_user=current_user,
        password_update=body,
    )
    user_public = UserPublic.model_validate(current_user)
    await send_password_changed_email(user_public)
    return create_response(
        status_code=status.HTTP_200_OK,
        message="Password updated successfully",
        request=request,
    )


@router.delete("/me")
async def delete_user_me(
    current_user: CurrentUser,
    user_service: UserServiceDep,
    request: Request,
) -> JSONResponse:
    """
    Delete current user.
    """
    await user_service.delete_user_me(current_user=current_user)
    user_public = UserPublic.model_validate(current_user)
    await send_delete_user_email(user_public)
    return create_response(
        status_code=status.HTTP_200_OK,
        message="User deleted successfully",
        request=request,
    )


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_by_id(
    current_superuser: CurrentSuperUser,
    user_id: ValidUUIDDep,
    user_service: UserServiceDep,
) -> UserPublic:
    """
    Get user by ID.
    """
    return await user_service.get_user_by_id(user_id=user_id)


@router.patch("/{user_id}", response_model=UserPublic)
async def update_user_by_id(
    current_superuser: CurrentSuperUser,
    user_in: UserUpdate,
    user_id: ValidUUIDDep,
    user_service: UserServiceDep,
) -> UserPublic:
    """
    Update user by ID.
    """
    updated_user = await user_service.update_user(
        current_user=current_superuser,
        user_id=user_id,
        user_in=user_in,
    )

    if user_in.password:
        user_public = UserPublic.model_validate(updated_user)
        await send_password_changed_email(user_public)
    return updated_user


@router.delete("/{user_id}")
async def delete_user_by_id(
    current_superuser: CurrentSuperUser,
    user_id: ValidUUIDDep,
    user_service: UserServiceDep,
    request: Request,
) -> JSONResponse:
    """
    Delete user by ID.
    """
    deleted_user = await user_service.delete_user_by_id(user_id=user_id)
    user_public = UserPublic.model_validate(deleted_user)
    await send_delete_user_email(user_public)
    return create_response(
        status_code=status.HTTP_200_OK,
        message="User deleted successfully",
        request=request,
    )
