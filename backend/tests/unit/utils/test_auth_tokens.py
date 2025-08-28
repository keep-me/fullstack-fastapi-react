"""
Unit tests for authentication token utilities.
"""

from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
import pytest

from app.core.config import settings
from app.models.domain.user import User
from app.models.schemas.token import Token
from app.repositories.unit_of_work import UnitOfWork
from app.utils.auth import (
    create_jwt,
    create_reset_jwt,
    create_tokens,
    validate_token,
    verify_reset_code,
)
from tests.parametrized_test_data import (
    validate_token_param_data,
)


def create_test_token(
    token_type: str,
    user_id: UUID,
    minutes_offset: int = 0,
    expired: bool = False,
) -> str:
    """
    Creates test tokens with various configurations.
    """
    iat = datetime.now().astimezone() - timedelta(minutes=minutes_offset)

    if expired:
        exp = iat + timedelta(minutes=1)
    else:
        exp = iat + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return create_jwt(token_type, user_id, iat, exp)


@pytest.mark.asyncio
async def test_create_tokens(db_session: Any, test_user: User) -> None:
    """
    Tests token creation functionality.
    """
    uow = UnitOfWork(db_session)
    result = await create_tokens(uow, test_user.id, "test_fingerprint")
    assert isinstance(result, Token)
    assert result.access_token
    assert result.refresh_token


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, token_type, minutes_offset, expired, expected_type, exception, expected_status_code, expected_message",
    validate_token_param_data,
    ids=["valid_data", "expired_token", "invalid_token"],
)
# fmt: on
async def test_validate_token(user_id: UUID, token_type: str, minutes_offset: int, expired: bool, expected_type: str, exception: Any, expected_status_code: int, expected_message: str) -> None:
    """
Tests token validation with various scenarios.
"""
    token = create_test_token(
        token_type, user_id, minutes_offset=minutes_offset, expired=expired,
    )

    if not exception:
        payload = validate_token(token, expected_type)
        assert payload.sub == user_id
    else:
        with pytest.raises(exception) as exc:
            validate_token(token, expected_type)

        assert exc.value.status_code == expected_status_code
        assert exc.value.error == expected_message


@pytest.mark.asyncio
async def test_create_reset_jwt(test_user_email: str) -> None:
    """
Tests reset JWT token creation functionality.
"""
    token = create_reset_jwt(test_user_email)

    assert token is not None
    assert isinstance(token, str)


    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    assert payload["sub"] == test_user_email
    assert payload["type"] == "password_reset"
    assert "exp" in payload
    assert "id" in payload


@pytest.mark.asyncio
async def test_verify_reset_code(test_user_email: str, monkeypatch: pytest.MonkeyPatch, redis_client: Any) -> None:
    """
Tests reset code verification functionality.
"""
    monkeypatch.setattr("app.utils.auth.redis_client", redis_client)
    code = "123456"

    await redis_client.setex(f"reset-token:{test_user_email}", 600, code)
    result = await verify_reset_code(test_user_email, code)
    assert result is True

    result = await verify_reset_code(test_user_email, "wrong123")
    assert result is False

    await redis_client.delete(f"reset-token:{test_user_email}")
    result = await verify_reset_code(test_user_email, code)
    assert result is False
