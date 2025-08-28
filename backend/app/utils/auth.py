"""
Authentication utilities for the application.
"""

import secrets
from datetime import datetime, timedelta
from uuid import UUID

import jwt

from app.core.config import settings
from app.core.exceptions import TokenError
from app.core.redis import redis_client
from app.models.schemas.token import Token, TokenPayload
from app.repositories.unit_of_work import UnitOfWork


def create_jwt(type: str, user_id: UUID, iat: datetime, exp: datetime) -> str:
    """
    Create JWT token for user authentication.
    """
    return jwt.encode(
        {
            "type": type,
            "sub": str(user_id),
            "iat": iat,
            "exp": exp,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


async def create_tokens(uow: UnitOfWork, user_id: UUID, fingerprint: str) -> Token:
    """
    Create access and refresh tokens for user.
    """
    iat = datetime.now().astimezone()

    access_exp = iat + settings.ACCESS_TOKEN_EXPIRE
    refresh_exp = iat + settings.REFRESH_TOKEN_EXPIRE

    access_token = create_jwt("access", user_id, iat, access_exp)
    refresh_token = create_jwt("refresh", user_id, iat, refresh_exp)

    await uow.sessions.create_or_update_session(
        uow.session,
        user_id,
        refresh_token,
        fingerprint,
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


def validate_token(token: str, expected_type: str) -> TokenPayload:
    """
    Validate JWT token and return payload data.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise TokenError(error_type="token_expired")
    except jwt.PyJWTError:
        raise TokenError(error_type="invalid_token")

    token_data = TokenPayload(**payload)

    if expected_type and payload.get("type") != expected_type:
        raise TokenError(error_type="invalid_token")
    return token_data


def create_reset_jwt(email: str) -> str:
    """
    Create JWT token for password reset.
    """
    payload = {
        "id": secrets.token_hex(8),
        "sub": email,
        "exp": datetime.utcnow()
        + timedelta(minutes=settings.RESET_CODE_EXPIRE_MINUTES),
        "type": "password_reset",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


async def verify_reset_code(email: str, code: str) -> bool:
    """
    Verify password reset code.
    """
    redis_key = f"reset-token:{email}"
    stored_code = await redis_client.get(redis_key)

    if not stored_code:
        return False

    return bool(stored_code.decode() == code)
