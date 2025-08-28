"""
Authentication service for the application.
"""

import logging
import secrets

import jwt
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import TokenError, UserAccessError, ValidationError
from app.core.redis import redis_client
from app.models.domain.role import RoleEnum
from app.models.domain.session import Session
from app.models.domain.user import User
from app.models.schemas.token import Token
from app.models.schemas.user import UserCreate, UserPublic, UserRegister
from app.repositories.unit_of_work import UnitOfWork
from app.utils.auth import (
    create_reset_jwt,
    create_tokens,
    validate_token,
    verify_reset_code,
)
from app.utils.notification import send_password_reset_email, send_welcome_email
from app.utils.password import verify_password
from app.utils.response import create_response

logger = logging.getLogger("app.auth_service")


class AuthService:
    """
    Service for handling authentication-related business logic.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.redis = redis_client

    async def register_user(self, user_in: UserRegister) -> User:
        """
        Register a new user in the system.
        """
        db_user = await self.uow.users.get_user(
            session=self.uow.session,
            username=user_in.username,
            email=user_in.email,
        )

        if db_user:
            error_type = (
                "username" if db_user.username == user_in.username.lower() else "email"
            )
            raise ValidationError(f"{error_type}_exists")

        user_create_data = user_in.model_dump()
        user_create_data["role"] = RoleEnum.USER
        user_create = UserCreate.model_construct(**user_create_data)

        new_user = await self.uow.users.create_user(
            session=self.uow.session,
            obj_in=user_create,
        )
        await send_welcome_email(UserPublic.model_validate(new_user))
        return new_user

    async def login(
        self,
        username: str,
        password: str,
        response: Response,
        fingerprint: str,
    ) -> Token:
        """
        Login user to the system.
        """
        if not username:
            raise UserAccessError("invalid_username")
        if not password:
            raise ValidationError("incorrect_password")

        db_user = await self.uow.users.get_user(
            session=self.uow.session,
            username=username,
        )

        if not db_user:
            raise UserAccessError("user_not_found")

        if not verify_password(password, str(db_user.hashed_password)):
            raise ValidationError("incorrect_password")

        if not db_user.is_active:
            raise UserAccessError("inactive")

        new_tokens = await create_tokens(
            uow=self.uow,
            user_id=db_user.id,
            fingerprint=fingerprint,
        )

        self._set_refresh_token_cookie(response, new_tokens.refresh_token)
        return new_tokens

    async def refresh_token(
        self,
        request: Request,
        fingerprint: str,
        response: Response,
    ) -> Token:
        """
        Refresh user authentication tokens.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise TokenError("no_session")

        try:
            access_token = auth_header.split()[-1]
        except IndexError:
            raise TokenError("invalid_header")

        refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIES_NAME)
        if not refresh_token:
            raise TokenError("no_session")

        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )

        user_id = payload.get("sub")

        refresh_token_data = validate_token(refresh_token, "refresh")

        stmt = (
            select(Session)
            .options(selectinload(Session.user))
            .where(Session.refresh_token == refresh_token)
        )
        result = await self.uow.session.execute(stmt)
        db_session = result.scalar_one_or_none()
        db_user = db_session.user if db_session else None

        if not db_session:
            raise TokenError("no_session")

        if (
            db_session.fingerprint != fingerprint
            or str(db_session.user_id) != str(user_id)
            or str(db_session.user_id) != str(refresh_token_data.sub)
        ):
            raise TokenError("invalid_ownership")

        if not db_user:
            raise TokenError("user_not_found")
        if not db_user.is_active:
            raise UserAccessError("inactive")

        new_tokens = await create_tokens(
            uow=self.uow,
            user_id=db_user.id,
            fingerprint=fingerprint,
        )

        self._set_refresh_token_cookie(response, new_tokens.refresh_token)
        return new_tokens

    async def logout(self, request: Request) -> Response:
        """
        Logout user from the system.
        """
        refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIES_NAME)
        if refresh_token:
            await self.uow.sessions.delete_by_refresh_token(
                session=self.uow.session,
                refresh_token=refresh_token,
            )
            message = "Successfully logged out"
        else:
            message = "Already logged out or no active session"

        response = create_response(
            message=message,
            request=request,
        )

        self._delete_refresh_token_cookie(response)

        return response

    async def request_reset_password(
        self,
        email: str,
        request: Request,
    ) -> JSONResponse:
        """
        Initiates password reset.
        """
        user = await self.uow.users.get_user(session=self.uow.session, email=email)
        if not user:
            raise UserAccessError(error_type="user_not_found")

        if not user.is_active:
            raise UserAccessError(error_type="inactive")

        code = str(secrets.randbelow(900000) + 100000)
        token = create_reset_jwt(email)

        redis_key = f"reset-token:{email}"
        expire_seconds = settings.RESET_CODE_EXPIRE_MINUTES * 60
        await self.redis.setex(redis_key, expire_seconds, code)

        user_public = UserPublic.model_validate(user)
        await send_password_reset_email(user_public, code)

        response = create_response(
            message=f"Verification code sent to {email}",
            request=request,
        )
        response.headers["X-Verification"] = token
        return response

    async def verify_code(
        self,
        email: str,
        code: str,
        request: Request,
    ) -> JSONResponse:
        """
        Verifies confirmation code.
        """
        if not await verify_reset_code(email, code):
            raise TokenError("not_verified")

        reset_token = request.headers.get("X-Verification", "")

        response = create_response(
            message="Code verified successfully",
            request=request,
        )
        response.headers["X-Verification"] = reset_token
        return response

    async def set_new_password(
        self,
        email: str,
        new_password: str,
        confirm_password: str,
        request: Request,
    ) -> JSONResponse:
        """
        Sets new password.
        """
        if new_password != confirm_password:
            raise ValidationError("passwords_not_match")

        redis_key = f"reset-token:{email}"
        if not await self.redis.exists(redis_key):
            raise TokenError("token_expired")

        user = await self.uow.users.get_user(session=self.uow.session, email=email)
        if not user:
            raise UserAccessError(error_type="user_not_found")

        await self.uow.users.update_password(
            session=self.uow.session,
            user=user,
            new_password=new_password,
        )

        await self.redis.delete(redis_key)

        return create_response(message="Password changed successfully", request=request)

    def _set_refresh_token_cookie(self, response: Response, refresh_token: str) -> None:
        """
        Set refresh token cookie in response.
        """
        response.set_cookie(
            key=settings.REFRESH_TOKEN_COOKIES_NAME,
            value=refresh_token,
            path="/",
            samesite="lax",
            secure=settings.COOKIE_SECURE,
            httponly=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )

    def _delete_refresh_token_cookie(self, response: Response) -> None:
        """
        Delete refresh token cookie from response.
        """
        response.delete_cookie(
            key=settings.REFRESH_TOKEN_COOKIES_NAME,
            path="/",
            samesite="lax",
            secure=settings.COOKIE_SECURE,
            httponly=True,
        )
