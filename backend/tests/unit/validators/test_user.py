"""
Unit tests for user validation utilities.
"""

from typing import Any

import pytest

from app.core.exceptions import HTTPException
from app.validators.user import EmailValidator, PasswordValidator, UsernameValidator
from tests.parametrized_test_data import (
    email_validator_param_data,
    password_update_validator_param_data,
    password_validator_param_data,
    username_validator_param_data,
)
from tests.utils import assert_exception


# fmt: off
@pytest.mark.parametrize(
    "username, expected_exception, expected_status_code, expected_message",
    username_validator_param_data,
    ids=["valid_user", "valid_user_123", "valid_user_underscore", "too_short", "too_long", "with_dash", "with_at", "with_space", "empty"],
)
# fmt: on
async def test_username_validator(username: str, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests username validation with various input patterns.
"""
    if not expected_exception:
        result = UsernameValidator.validate(username)
        assert result == username
    else:
        with pytest.raises(expected_exception) as exc:
            UsernameValidator.validate(username)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)


# fmt: off
@pytest.mark.parametrize(
    "email, expected_exception, expected_status_code, expected_message",
    email_validator_param_data,
    ids=["valid_email", "valid_email_subdomain", "valid_email_plus", "invalid_format", "no_local_part", "no_domain", "no_at_symbol", "empty"],
)
# fmt: on
async def test_email_validator(email: str, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests email validation with various input formats.
"""
    if not expected_exception:
        result = EmailValidator.validate(email)
        assert result is not None
        assert "@" in result
    else:
        with pytest.raises(expected_exception) as exc:
            EmailValidator.validate(email)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)


# fmt: off
@pytest.mark.parametrize(
    "password, expected_exception, expected_status_code, expected_message",
    password_validator_param_data,
    ids=["valid_password", "valid_numbers", "valid_long", "too_short", "empty"],
)
# fmt: on
async def test_password_validator(password: str, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests password validation with various input patterns.
"""
    if not expected_exception:
        result = PasswordValidator.validate(password)
        assert result == password
    else:
        with pytest.raises(expected_exception) as exc:
            PasswordValidator.validate(password)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)


# fmt: off
@pytest.mark.parametrize(
    "current_password, new_password, hashed_current, expected_exception, expected_status_code, expected_message",
    password_update_validator_param_data,
    ids=["valid_update", "incorrect_current", "same_passwords", "new_too_short", "password_not_set"],
)
# fmt: on
async def test_password_update_validator(current_password: str, new_password: str, hashed_current: str, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str, monkeypatch: Any) -> None:
    """
Tests password update validation with various scenarios.
"""

    def mock_verify_password(plain_password: str, hashed_password: str) -> bool:
        if hashed_password == "hashed_current":
            return plain_password == "CurrentPass123"
        return False

    monkeypatch.setattr("app.utils.password.verify_password", mock_verify_password)

    if not expected_exception:
        result = PasswordValidator.validate_update(current_password, new_password, hashed_current)
        assert result == new_password
    else:
        with pytest.raises(expected_exception) as exc:
            PasswordValidator.validate_update(current_password, new_password, hashed_current)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)
