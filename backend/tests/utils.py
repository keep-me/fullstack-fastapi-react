from datetime import datetime
from typing import Any
from uuid import UUID

import pytest
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import HTTPException
from app.repositories.base import BaseRepository
from app.repositories.session import session_repo
from app.utils.auth import create_jwt


class _TestModel:
    """
    Simple test model for testing.
    """

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)


class _TestCreateSchema(BaseModel):
    """
    Test creation schema.
    """

    name: str
    password: str | None = None


class _TestUpdateSchema(BaseModel):
    """
    Test update schema.
    """

    name: str | None = None


class _TestRepository(BaseRepository[_TestModel, _TestCreateSchema, _TestUpdateSchema]):
    """
    Test repository implementation.
    """

    def __init__(self) -> None:
        super().__init__(_TestModel)


async def assert_http_response(
    exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    with pytest.raises(exception) as exc:
        raise exception(error_type)
    assert exc.value.status_code == expected_status_code
    assert exc.value.message == expected_message


async def assert_exception(
    called_exc: HTTPException,
    expected_exception: type[HTTPException],
    expected_status_code: int,
    expected_message: str,
) -> None:
    assert isinstance(called_exc, expected_exception)
    assert called_exc.status_code == expected_status_code
    assert called_exc.message == expected_message


async def generate_cache_key(user_id: UUID) -> str:
    return f"user:id:{user_id}"


def create_test_refresh_token(user_id: UUID) -> str:
    """
    Generate a test refresh token.
    """
    iat = datetime.now().astimezone()
    exp = iat + settings.REFRESH_TOKEN_EXPIRE
    return create_jwt("refresh", user_id, iat, exp)


async def create_test_session(
    db_session: AsyncSession,
    user_id: UUID,
    fingerprint: str | None = None,
) -> Any:
    """
    Create a test session with generated refresh token.
    """
    if not fingerprint:
        fingerprint = "test-fingerprint"
    refresh_token = create_test_refresh_token(user_id)

    session = await session_repo.create_or_update_session(
        db_session,
        user_id,
        refresh_token,
        fingerprint,
    )
    return session, refresh_token, fingerprint


def assert_session_matches(
    session: Any,
    user_id: UUID,
    refresh_token: str,
    fingerprint: str,
) -> None:
    """
    Assert that session properties match expected values.
    """
    assert session is not None
    assert session.user_id == user_id
    assert session.refresh_token == refresh_token
    assert session.fingerprint == fingerprint
    assert session.expires_at is not None
