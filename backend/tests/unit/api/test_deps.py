"""
Unit tests for dependency functions.
"""

from typing import Any
from uuid import uuid4

import pytest

from app.api.deps import (
    get_current_active_superuser,
    get_current_user,
    pagination_params,
    validate_user_id,
)
from app.core.exceptions import HTTPException
from app.models.domain.role import Role, RoleEnum
from app.models.domain.user import User
from tests.parametrized_test_data import (
    deps_get_current_active_superuser_param_data,
    deps_get_current_user_param_data,
    deps_pagination_params_param_data,
    deps_validate_user_id_param_data,
)
from tests.utils import assert_exception


# fmt: off
@pytest.mark.parametrize(
    "user_id, expected_exception, expected_status_code, expected_message",
    deps_validate_user_id_param_data,
    ids=["valid_uuid", "invalid_uuid"],
)
# fmt: on
async def test_validate_user_id(
    user_id: str,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests user ID validation.
"""
    if not expected_exception:
        assert isinstance(validate_user_id(str(user_id)), uuid4().__class__)
    else:
        with pytest.raises(expected_exception) as exc:
            validate_user_id(user_id)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token, token_data_sub, user_exists, user_active, expected_exception, expected_status_code, expected_message",
    deps_get_current_user_param_data,
    ids=["valid_user", "no_token", "invalid_token", "user_not_found", "user_inactive"],
)
# fmt: on
async def test_get_current_user(
    monkeypatch: pytest.MonkeyPatch,
    token: str,
    token_data_sub: str,
    user_exists: bool,
    user_active: bool,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    uow: Any,
    mock_redis_client: Any,
) -> None:
    """
Tests getting current user from token.
"""
    def fake_validate_token(token: str, typ: str) -> Any:
        class Data:
            sub = token_data_sub

        return Data()

    monkeypatch.setattr("app.api.deps.validate_token", fake_validate_token)

    if not expected_exception:
        user = await get_current_user(token=token, uow=uow)
        assert user.is_active is True
    else:
        with pytest.raises(expected_exception) as exc:
            await get_current_user(token=token, uow=uow)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role_name, expected_exception, expected_status_code, expected_message",
    deps_get_current_active_superuser_param_data,
    ids=["admin", "user"],
)
# fmt: on
async def test_get_current_active_superuser(
    role_name: RoleEnum,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests getting current active superuser.
"""
    role = Role(id=1, name=role_name) # type: ignore[call-arg]
    user = User(id=uuid4(), username="newtestuser", email="newtestuser@example.com", full_name="newtestuser", hashed_password="Password123", is_active=True, role=role, role_id=1) # type: ignore[call-arg]

    if not expected_exception:
        result = await get_current_active_superuser(user)
        assert result.is_active
        assert result.role.name == RoleEnum.ADMIN
    else:
        with pytest.raises(expected_exception) as exc:
            await get_current_active_superuser(user)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "skip, limit, expected_limit, expected_exception, expected_status_code, expected_message",
    deps_pagination_params_param_data,
    ids=["max_limit", "custom_limit", "invalid_skip", "invalid_limit", "invalid_pagination"],
)
# fmt: on
async def test_pagination_params_limit(
    skip: int,
    limit: int,
    expected_limit: int,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests pagination parameters validation.
"""
    if not expected_exception:
        params = await pagination_params(skip=skip, limit=limit)
        assert params.limit == expected_limit
    else:
        with pytest.raises(expected_exception) as exc:
            await pagination_params(skip=skip, limit=limit)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)
