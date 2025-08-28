"""
Unit tests for authentication endpoints.
"""

from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient

from app.core.exceptions import HTTPException
from tests.parametrized_test_data import (
    login_user_param_data,
    logout_user_param_data,
    refresh_token_param_data,
    register_user_param_data,
    reset_password_param_data,
    set_new_password_param_data,
    verify_code_param_data,
)
from tests.utils import assert_http_response


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, exception, error_type, expected_status_code, expected_message",
    register_user_param_data,
    ids=["valid_data", "empty_username", "existing_username", "empty_email", "invalid_email", "existing_email", "empty_password"],
)
# fmt: on
async def test_register_user(
    async_client: AsyncClient,
    user_data: dict[str, Any] | None,
    exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
    random_user_data: dict[str, Any],
    mock_send_email: AsyncMock,
) -> None:
    """
Tests user registration endpoint.
"""
    if isinstance(user_data, dict):
        random_user_data.update(user_data)

    response = await async_client.post("/api/v1/auth/signup", json=random_user_data)

    if not exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert set(["username", "email", "full_name"]).issubset(data)
        assert data["username"] == random_user_data["username"].lower()
        assert data["email"] == random_user_data["email"].lower()
        assert data["full_name"] == random_user_data["full_name"]
        mock_send_email.assert_awaited_once()
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, fingerprint, exception, error_type, expected_status_code, expected_message",
    login_user_param_data,
    ids=["valid_data", "nonexistent_user", "wrong_password", "inactive_user", "empty_username", "empty_password"],
)
# fmt: on
async def test_login(
    async_client: AsyncClient,
    username: str,
    password: str,
    fingerprint: str,
    exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests user login endpoint.
"""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password, "fingerprint": fingerprint},
    )

    if not exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert set(["access_token", "refresh_token", "token_type"]).issubset(data)
        assert data["token_type"] == "bearer"
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "headers, exception, error_type, expected_status_code, expected_message",
    logout_user_param_data,
    ids=["valid_data", "empty_headers", "no_headers", "invalid_token"],
)
# fmt: on
async def test_logout(
    async_client: AsyncClient,
    headers: dict[str, str],
    exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests user logout endpoint.
"""
    response = await async_client.get("/api/v1/auth/logout", headers=headers)

    if not exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert "message" in data
        assert data["message"] == expected_message
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case, fingerprint, exception, error_type, expected_status_code, expected_message",
    refresh_token_param_data,
    ids=["valid", "no_cookie", "invalid_cookie", "invalid_fingerprint", "no_header", "invalid_header"],
)
# fmt: on
async def test_refresh_token(
    async_client: AsyncClient,
    test_user: Any,
    case: str,
    fingerprint: str,
    exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests token refresh endpoint.
"""
    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"username": test_user.username, "password": "Password123", "fingerprint": "initial_fingerprint"},
    )
    assert login_response.status_code == status.HTTP_200_OK
    login_data = login_response.json()

    valid_access_token = login_data["access_token"]
    valid_refresh_token = login_data["refresh_token"]

    headers = {"Authorization": f"Bearer {valid_access_token}"}
    async_client.cookies.set("refresh_token", valid_refresh_token)

    match case:
        case "no_cookie":
            async_client.cookies.clear()
        case "invalid_cookie":
            async_client.cookies.set("refresh_token", "invalid_token")
        case "no_header":
            headers = {}
        case "invalid_header":
            headers["Authorization"] = "Bearer invalid.token"

    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"fingerprint": fingerprint},
        headers=headers,
    )

    if not exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert set(["access_token", "refresh_token", "token_type"]).issubset(data)
        assert data["token_type"] == "bearer"
    else:
        await assert_http_response(exception, error_type, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, expected_exception, error_type, expected_status_code, expected_message",
    reset_password_param_data,
    ids=["valid_email", "nonexistent_email", "inactive_user"],
)
# fmt: on
async def test_reset_password(
    async_client: AsyncClient,
    test_user: Any,
    mock_send_email: AsyncMock,
    email: str,
    expected_exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests password reset endpoint.
"""
    response = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"email": email},
    )

    if not expected_exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert "message" in data
        assert expected_message in data["message"]
        assert "X-Verification" in response.headers
        mock_send_email.assert_awaited_once()
    else:
        await assert_http_response(expected_exception, error_type, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "code, expected_exception, error_type, expected_status_code, expected_message",
    verify_code_param_data,
    ids=["valid_code", "invalid_code", "empty_code"],
)
# fmt: on
async def test_verify_code(
    async_client: AsyncClient,
    test_user: Any,
    mock_redis_client: Any,
    code: str,
    expected_exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests verification code endpoint.
"""
    reset_response = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"email": test_user.email},
    )

    verification_token = reset_response.headers["X-Verification"]

    await mock_redis_client.setex(f"reset-token:{test_user.email}", 600, "123456")

    response = await async_client.post(
        "/api/v1/auth/verify-code",
        json={"code": code},
        headers={"X-Verification": verification_token},
    )

    if not expected_exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert "message" in data
        assert expected_message in data["message"]
        assert "X-Verification" in response.headers
    else:
        await assert_http_response(expected_exception, error_type, expected_status_code, expected_message)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "new_password, confirm_password, expected_exception, error_type, expected_status_code, expected_message",
    set_new_password_param_data,
    ids=["valid_passwords", "passwords_not_match", "invalid_token", "empty_passwords"],
)
# fmt: on
async def test_set_new_password(
    async_client: AsyncClient,
    test_user: Any,
    mock_redis_client: Any,
    new_password: str,
    confirm_password: str,
    expected_exception: type[HTTPException],
    error_type: Any,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests setting new password endpoint.
"""
    reset_response = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"email": test_user.email},
    )

    verification_token = reset_response.headers["X-Verification"]

    await mock_redis_client.setex(f"reset-token:{test_user.email}", 600, "123456")

    await async_client.post(
        "/api/v1/auth/verify-code",
        json={"code": "123456"},
        headers={"X-Verification": verification_token},
    )

    response = await async_client.post(
        "/api/v1/auth/new-password",
        json={
            "new_password": new_password,
            "confirm_new_password": confirm_password,
        },
        headers={"X-Verification": verification_token},
    )

    if not expected_exception:
        assert response.status_code == expected_status_code
        data = response.json()
        assert "message" in data
        assert data["message"] == expected_message
    else:
        await assert_http_response(expected_exception, error_type, expected_status_code, expected_message)
