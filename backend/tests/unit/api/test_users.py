"""
Unit tests for user endpoints.
"""

from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.exceptions import HTTPException
from app.models.domain.role import RoleEnum
from app.models.schemas.user import UserPublic
from tests.parametrized_test_data import (
    create_user_param_data,
    delete_user_by_id_param_data,
    delete_user_me_param_data,
    get_user_by_id_param_data,
    get_users_param_data,
    update_password_me_param_data,
    update_user_by_id_param_data,
    update_user_me_param_data,
)
from tests.utils import assert_http_response


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, expected_status_code, exception, error_type, expected_message, extra_user_data",
    create_user_param_data,
    ids=["valid_data", "unauthorized_access", "empty_username", "username_is_none", "username_too_short", "username_too_long", "username_special_chars", "empty_email", "email_is_none", "invalid_email_format", "invalid_email_no_local", "invalid_email_no_domain", "empty_password", "password_is_none", "password_too_short", "admin_true", "not_admin", "active", "not_active", "empty_full_name", "long_full_name", "existing_username", "existing_email"],
)
# fmt: on
async def test_create_user(
    async_client: AsyncClient,
    headers: dict[str, str],
    expected_status_code: int,
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_message: str,
    random_user_data: dict[str, Any],
    extra_user_data: dict[str, Any],
    mock_send_email: AsyncMock,
) -> None:
    """
Tests user creation endpoint.
"""
    random_user_data.update(extra_user_data)

    response = await async_client.post(
        "/api/v1/users/", json=random_user_data, headers=headers,
    )
    if not exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert set(
            ["id", "username", "email", "full_name", "is_active", "role"],
        ).issubset(data)
        assert data["username"] == random_user_data["username"]
        assert data["email"] == random_user_data["email"]
        assert data["full_name"] == random_user_data["full_name"]
        assert data["role"] == random_user_data["role"]
        assert data["is_active"] == random_user_data["is_active"]
        mock_send_email.assert_awaited_once()
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_user_me(
    async_client: AsyncClient,
    test_user: Any,
    login_and_get_headers_test_user: dict[str, str],
) -> None:
    """
Tests getting current user profile endpoint.
"""
    response = await async_client.get(
        "/api/v1/users/me", headers=login_and_get_headers_test_user,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert set(["username", "email", "full_name", "role", "is_active"]).issubset(data)
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert data["role"] == str(test_user.role)
    assert data["is_active"] == test_user.is_active


@pytest.mark.asyncio
async def test_get_my_id(
    async_client: AsyncClient,
    test_user: Any,
    login_and_get_headers_test_user: dict[str, str],
) -> None:
    """
Tests getting current user ID endpoint.
"""
    response = await async_client.get(
        "/api/v1/users/my_id", headers=login_and_get_headers_test_user,
    )
    assert response.status_code == status.HTTP_200_OK
    user_id = response.json()
    assert UUID(user_id) == test_user.id

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, expected_status_code, exception, error_type, expected_message",
    get_users_param_data,
    ids=["valid_data", "not_admin"],
)
# fmt: on
async def test_get_users(
    async_client: AsyncClient,
    headers: dict[str, str],
    expected_status_code: int,
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_message: str,
) -> None:
    """
Tests getting all users endpoint.
"""
    response = await async_client.get("/api/v1/users/", headers=headers)
    assert response.status_code == expected_status_code
    if not exception:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert set(
            ["id", "username", "email", "full_name", "role", "is_active"],
        ).issubset(data[0])
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "updated_data, exception, error_type, expected_status_code, expected_message",
    update_user_me_param_data,
    ids=["valid_username", "existing_username", "invalid_username_short", "empty_username", "invalid_username_long", "invalid_username_special", "valid_email", "existing_email", "invalid_email", "empty_email", "invalid_email_no_local", "invalid_email_no_domain", "valid_full_name", "empty_full_name", "long_full_name"],
)
# fmt: on
async def test_update_user_me(
    async_client: AsyncClient,
    test_user: Any,
    login_and_get_headers_test_user: dict[str, str],
    updated_data: dict[str, Any],
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests updating current user profile endpoint.
"""
    response = await async_client.patch(
        "/api/v1/users/me", json=updated_data, headers=login_and_get_headers_test_user,
    )
    for k, v in updated_data.items():
        if hasattr(test_user, k):
            setattr(test_user, k, v)

    if not exception:
        data = response.json()
        assert set(["username", "email", "full_name"]).issubset(data)
        assert data["username"] == test_user.username.lower()
        assert data["email"] == test_user.email.lower()
        assert data["full_name"] == test_user.full_name
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "password_data, exception, error_type, expected_status_code, expected_message",
    update_password_me_param_data,
    ids=["valid_data", "empty_new_password", "short_new_password", "same_passwords", "incorrect_password", "empty_current_password"],
)
# fmt: on
async def test_update_password_me(
    async_client: AsyncClient,
    test_user: Any,
    login_and_get_headers_test_user: dict[str, str],
    password_data: dict[str, str],
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
    mock_send_email: AsyncMock,
) -> None:
    """
Tests updating current user password endpoint.
"""
    response = await async_client.patch(
        "/api/v1/users/me/password",
        json=password_data,
        headers=login_and_get_headers_test_user,
    )
    if not exception:
        data = response.json()
        assert "message" in data
        assert data["message"] == expected_message
        mock_send_email.assert_awaited_once()
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, expected_status_code, exception, error_type, expected_message",
    delete_user_me_param_data,
    ids=["normal_user", "admin"],
)
# fmt: on
async def test_delete_user_me(
    async_client: AsyncClient,
    headers: dict[str, str],
    expected_status_code: int,
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_message: str,
    mock_send_email: AsyncMock,
) -> None:
    """
Tests deleting current user endpoint.
"""
    response = await async_client.delete("/api/v1/users/me", headers=headers)

    if not exception:
        data = response.json()
        assert "message" in data
        assert data["message"] == expected_message
        mock_send_email.assert_awaited_once()
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, id_param, exception, error_type, expected_status_code, expected_message",
    get_user_by_id_param_data,
    ids=["valid_id", "not_admin_access", "invalid_id"],
)
# fmt: on
async def test_get_user_by_id(
    async_client: AsyncClient,
    test_user: Any,
    headers: dict[str, str],
    id_param: str,
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests getting user by ID endpoint.
"""
    response = await async_client.get(f"/api/v1/users/{id_param}", headers=headers)
    assert response.status_code == expected_status_code
    if not exception:
        data = response.json()
        assert set(
            ["id", "username", "email", "full_name", "role", "is_active"],
        ).issubset(data)
        assert data["id"] == str(test_user.id)
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["role"] == str(test_user.role)
        assert data["is_active"] == test_user.is_active
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, id_param, updated_data, exception, error_type, expected_status_code, expected_message",
    update_user_by_id_param_data,
    ids=["valid_new_username", "empty_new_username", "valid_new_email", "empty_new_email", "invalid_new_email", "valid_new_full_name", "active_false", "active_true", "role_user", "role_admin", "invalid_role", "valid_new_password", "not_admin_access", "invalid_id", "existing_username"],
)
# fmt: on
async def test_update_user_by_id(
    async_client: AsyncClient,
    test_user: Any,
    headers: dict[str, str],
    id_param: str,
    updated_data: dict[str, Any],
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
    mock_send_email: AsyncMock,
) -> None:
    """
Tests updating user by ID endpoint.
"""
    response = await async_client.patch(
        f"/api/v1/users/{id_param}", json=updated_data, headers=headers,
    )

    if not exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert set(
            ["id", "username", "email", "full_name", "role", "is_active"],
        ).issubset(data)

        expected_data = UserPublic.model_validate(test_user).model_dump()
        for key, value in updated_data.items():
            if key == "role":
                if isinstance(value, RoleEnum):
                    expected_data[key] = value.value
                else:
                    expected_data[key] = value
            elif key in ("username", "email") and isinstance(value, str):
                expected_data[key] = value.lower()
            else:
                expected_data[key] = value

        assert data["username"] == expected_data["username"]
        assert data["email"] == expected_data["email"]
        assert data["full_name"] == expected_data["full_name"]
        assert data["is_active"] == expected_data["is_active"]
        assert data["role"] == expected_data["role"]
        if "password" in updated_data:
            mock_send_email.assert_awaited_once()
        else:
            mock_send_email.assert_not_awaited()
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, id_param, exception, error_type, expected_status_code, expected_message",
    delete_user_by_id_param_data,
    ids=["valid_id", "not_admin_access", "invalid_id"],
)
# fmt: on
async def test_delete_user_by_id(
    async_client: AsyncClient,
    headers: dict[str, str],
    id_param: str,
    exception: type[HTTPException] | None,
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
    mock_send_email: AsyncMock,
) -> None:
    """
Tests deleting user by ID endpoint.
"""
    response = await async_client.delete(f"/api/v1/users/{id_param}", headers=headers)

    if not exception:
        data = response.json()
        assert "message" in data
        assert data["message"] == expected_message
        mock_send_email.assert_awaited_once()
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()
