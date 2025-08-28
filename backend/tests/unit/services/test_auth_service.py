"""
Unit tests for authentication service functionality.
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request, Response, status

from app.core.exceptions import HTTPException
from app.models.schemas.user import UserRegister
from app.repositories.unit_of_work import UnitOfWork
from app.services.auth_service import AuthService
from tests.parametrized_test_data import (
    auth_service_login_user_param_data,
    auth_service_logout_param_data,
    auth_service_refresh_token_param_data,
    auth_service_register_user_param_data,
    auth_service_request_reset_password_param_data,
    auth_service_set_new_password_param_data,
    auth_service_verify_code_param_data,
)
from tests.utils import assert_exception


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_in_data, expected_exception, expected_status_code, expected_message",
    auth_service_register_user_param_data,
    ids=["success", "username_exists", "email_exists"],
)
# fmt: on
async def test_register_user(
    uow: UnitOfWork,
    user_in_data: dict[str, Any],
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_send_email: Any,
    mock_redis_client: Any,
) -> None:
    """
Tests user registration process with various scenarios.
"""
    auth_service = AuthService(uow)
    user_in = UserRegister(**user_in_data)

    if not expected_exception:
        new_user = await auth_service.register_user(user_in)
        mock_send_email.assert_awaited_once()
        assert new_user is not None
        assert new_user.username == user_in.username
    else:
        with pytest.raises(expected_exception) as exc:
            await auth_service.register_user(user_in)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)
        mock_send_email.assert_not_awaited()


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username, password, expected_exception, expected_status_code, expected_message",
    auth_service_login_user_param_data,
    ids=["valid_data", "nonexistent_user", "wrong_password", "inactive_user", "empty_username", "empty_password"],
)
# fmt: on
async def test_login_user(
    uow: UnitOfWork,
    username: str,
    password: str,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests user login functionality with various credentials.
"""
    auth_service = AuthService(uow)
    response = Response()

    if not expected_exception:
        data = await auth_service.login(
        username=username,
        password=password,
        response=response,
        fingerprint="test_fingerprint",
        )
        assert set(["access_token", "refresh_token", "token_type"]).issubset(data.model_dump().keys())
        assert data.access_token is not None
        assert data.refresh_token is not None
    else:
        with pytest.raises(expected_exception) as exc:
            await auth_service.login(
            username=username,
            password=password,
            response=response,
            fingerprint="test_fingerprint",
        )
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "refresh_token, expected_message, should_login_first",
    auth_service_logout_param_data,
    ids=["with_token", "without_token", "invalid_token"],
)
# fmt: on
async def test_logout(
    uow: UnitOfWork,
    test_user: Any,
    refresh_token: str,
    expected_message: str,
    should_login_first: bool,
    mock_redis_client: Any,
) -> None:
    """
Tests user logout functionality with different token scenarios.
"""
    auth_service = AuthService(uow)

    if should_login_first:
        login_response = Response()
        tokens = await auth_service.login(
            username=test_user.username,
            password="Password123",
            response=login_response,
            fingerprint="test_fingerprint",
        )
        refresh_token = tokens.refresh_token

        session = await uow.sessions.get_by_refresh_token(uow.session, refresh_token)
        assert session is not None

    mock_request = MagicMock(spec=Request)

    if should_login_first:
        mock_request.cookies.get.return_value = refresh_token
    elif refresh_token == "invalid_token":
        mock_request.cookies.get.return_value = "invalid_token"
    else:
        mock_request.cookies.get.return_value = None

    response = await auth_service.logout(mock_request)
    assert response.status_code == status.HTTP_200_OK

    data = json.loads(bytes(response.body).decode())
    assert data["message"] == expected_message

    if should_login_first:
        session_after_logout = await uow.sessions.get_by_refresh_token(
            uow.session, refresh_token,
        )
        assert session_after_logout is None

        set_cookie_header = response.headers.get("set-cookie", "")
        assert "refresh_token" in set_cookie_header
        assert "max-age=0" in set_cookie_header.lower()

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case, expected_exception, expected_status_code, expected_message",
    auth_service_refresh_token_param_data,
    ids=["success", "no_session", "no_auth_header", "invalid_auth_header", "no_refresh_cookie"],
)
# fmt: on
async def test_refresh_token(
    uow: UnitOfWork,
    test_user: Any,
    case: str,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests token refresh functionality with various scenarios.
"""
    auth_service = AuthService(uow)

    if case == "success":
        login_response = Response()
        initial_tokens = await auth_service.login(
            username=test_user.username,
            password="Password123",
            response=login_response,
            fingerprint="fingerprint",
        )

        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = f"Bearer {initial_tokens.access_token}"
        mock_request.cookies.get.return_value = initial_tokens.refresh_token
    elif case == "no_auth_header":
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = None
        mock_request.cookies.get.return_value = "some_refresh_token"
    elif case == "invalid_auth_header":
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = ""
        mock_request.cookies.get.return_value = "some_refresh_token"
    elif case == "no_refresh_cookie":
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "Bearer some_token"
        mock_request.cookies.get.return_value = None
    else:
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "Bearer some_token"
        mock_request.cookies.get.return_value = None

    refresh_response = Response()

    if expected_exception:
        with pytest.raises(expected_exception) as exc:
            await auth_service.refresh_token(
                request=mock_request,
                fingerprint="fingerprint",
                response=refresh_response,
            )
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)
    else:
        new_tokens = await auth_service.refresh_token(
            request=mock_request,
            fingerprint="fingerprint",
            response=refresh_response,
        )

        assert new_tokens.access_token is not None
        assert new_tokens.refresh_token is not None

        set_cookie_header = refresh_response.headers.get("set-cookie", "")
        assert "refresh_token" in set_cookie_header


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, expected_exception, expected_status_code, expected_message",
    auth_service_request_reset_password_param_data,
    ids=["valid_email", "nonexistent_email", "inactive_user"],
)
# fmt: on
async def test_request_reset_password(
    uow: UnitOfWork,
    test_user: Any,
    email: Any,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_send_email: AsyncMock,
    mock_redis_client: Any,
) -> None:
    """
Tests password reset request functionality.
"""
    auth_service = AuthService(uow)
    auth_service.redis = mock_redis_client

    mock_request = MagicMock()

    if not expected_exception:
        response = await auth_service.request_reset_password(email, mock_request)
        assert response.status_code == expected_status_code
        assert "X-Verification" in response.headers
        mock_send_email.assert_awaited_once()
    else:
        with pytest.raises(expected_exception) as exc:
            await auth_service.request_reset_password(email, mock_request)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "code, expected_exception, expected_status_code, expected_message",
    auth_service_verify_code_param_data,
    ids=["valid_code", "invalid_code"],
)
# fmt: on
async def test_verify_code(
    uow: UnitOfWork,
    test_user: Any,
    mock_redis_client: Any,
    code: str,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests verification code validation.
"""
    auth_service = AuthService(uow)
    auth_service.redis = mock_redis_client

    mock_request = MagicMock()
    mock_request.headers.get.return_value = "test_verification_token"

    await mock_redis_client.setex(f"reset-token:{test_user.email}", 600, "123456")

    if not expected_exception:
        response = await auth_service.verify_code(test_user.email, code, mock_request)
        assert response.status_code == expected_status_code

        data = json.loads(bytes(response.body).decode())
        assert data["message"] == expected_message
        assert "X-Verification" in response.headers
    else:
        with pytest.raises(expected_exception) as exc:
            await auth_service.verify_code(test_user.email, code, mock_request)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "new_password, confirm_password, has_valid_session, expected_exception, expected_status_code, expected_message",
    auth_service_set_new_password_param_data,
    ids=["valid_password_change", "passwords_not_match", "expired_session"],
)
# fmt: on
async def test_set_new_password(
    uow: UnitOfWork,
    test_user: Any,
    mock_redis_client: Any,
    new_password: str,
    confirm_password: str,
    has_valid_session: bool,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
) -> None:
    """
Tests setting new password functionality.
"""
    auth_service = AuthService(uow)
    auth_service.redis = mock_redis_client
    mock_request = MagicMock()

    redis_key = f"reset-token:{test_user.email}"
    if has_valid_session:
        await mock_redis_client.setex(redis_key, 600, "valid_session")
    else:
        await mock_redis_client.delete(redis_key)

    if not expected_exception:
        response = await auth_service.set_new_password(
            test_user.email,
            new_password,
            confirm_password,
            mock_request,
        )
        assert response.status_code == expected_status_code

        data = json.loads(bytes(response.body).decode())
        assert data["message"] == expected_message
    else:
        with pytest.raises(expected_exception) as exc:
            await auth_service.set_new_password(
                test_user.email,
                new_password,
                confirm_password,
                mock_request,
            )
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)
