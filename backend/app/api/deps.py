"""
Dependency functions for API endpoints.
"""

import logging
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.core.exceptions import TokenError, UserAccessError, ValidationError
from app.models.domain.user import User
from app.models.schemas.pagination import PaginationParams
from app.repositories.unit_of_work import UnitOfWork, get_uow
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.auth import validate_token

logger = logging.getLogger("app.api.deps")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def get_auth_service(uow: UnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow)


def validate_user_id(user_id: str) -> UUID:
    """
    Validate user_id string and convert to UUID.
    """
    try:
        return UUID(user_id)
    except (ValueError, TypeError):
        raise ValidationError("invalid_uuid")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    uow: UnitOfWork = Depends(get_uow),
) -> Any:
    """
    Get current user from token.
    """
    if not token:
        logger.warning("No token provided")
        raise TokenError(error_type="not_found")

    token_data = validate_token(token, "access")

    if not token_data.sub:
        logger.warning("Token does not contain user_id")
        raise TokenError(error_type="invalid_user_id")

    user = await uow.users.get_by_user_id(session=uow.session, user_id=token_data.sub)

    if not user:
        logger.warning(f"User not found for token: {token_data.sub}")
        raise TokenError(error_type="user_not_found")

    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.id}")
        raise UserAccessError(error_type="inactive")

    return user


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active superuser.
    """
    if not current_user.is_admin:
        logger.warning(f"Non-admin user attempted admin action: {current_user.id}")
        raise UserAccessError(error_type="not_admin")
    return current_user


def require_permission(permission_name: str):
    """
    Dependency factory for checking if a user has a specific permission.
    Admin users have all permissions.
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not current_user.has_permission(permission_name):
            logger.warning(
                f"User {current_user.id} attempted action without permission: {permission_name}"
            )
            raise UserAccessError(error_type="insufficient_permissions")
        return current_user

    return permission_checker


def require_any_permission(permission_names: list[str]):
    """
    Dependency factory for checking if a user has any of the specified permissions.
    Admin users have all permissions.
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not current_user.has_any_permission(permission_names):
            logger.warning(
                f"User {current_user.id} attempted action without any of permissions: {permission_names}"
            )
            raise UserAccessError(error_type="insufficient_permissions")
        return current_user

    return permission_checker


def require_all_permissions(permission_names: list[str]):
    """
    Dependency factory for checking if a user has all of the specified permissions.
    Admin users have all permissions.
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if not current_user.has_all_permissions(permission_names):
            logger.warning(
                f"User {current_user.id} attempted action without all permissions: {permission_names}"
            )
            raise UserAccessError(error_type="insufficient_permissions")
        return current_user

    return permission_checker


def require_role(role_name: str):
    """
    Dependency factory for checking if a user has a specific role.
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role is None or current_user.role.name != role_name:
            logger.warning(
                f"User {current_user.id} attempted action without role: {role_name}"
            )
            raise UserAccessError(error_type="insufficient_permissions")
        return current_user

    return role_checker


async def pagination_params(skip: int = 0, limit: int = 100) -> PaginationParams:
    """
    Get pagination parameters.
    """
    if skip < 0 or limit <= 0:
        raise ValidationError("invalid_pagination")
    return PaginationParams(skip=skip, limit=min(limit, 100))


async def get_reset_token_email(
    reset_token: str | None = Header(None, alias="X-Verification"),
) -> Any:
    """
    Get email from password reset JWT token.
    """
    if not reset_token:
        raise TokenError("not_found")

    payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=["HS256"])

    if payload.get("type") != "password_reset":
        raise TokenError("invalid_token_type")

    return payload["sub"]


ValidUUIDDep = Annotated[UUID, Depends(validate_user_id)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
UnitOfWorkDep = Annotated[UnitOfWork, Depends(get_uow)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSuperUser = Annotated[User, Depends(get_current_active_superuser)]
PaginationDep = Annotated[PaginationParams, Depends(pagination_params)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ResetEmailDep = Annotated[str, Depends(get_reset_token_email)]
