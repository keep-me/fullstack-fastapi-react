"""
Unit tests for password utilities.
"""

from collections.abc import Callable
from typing import Any

import pytest

from app.utils.password import (
    get_password_hash_async,
    get_password_hash_fast,
    get_password_hash_fast_async,
    verify_password,
)
from tests.parametrized_test_data import (
    password_hashing_consistency_param_data,
    verify_password_param_data,
)


@pytest.mark.asyncio
async def test_get_password_hash_async() -> None:
    """
    Tests asynchronous password hashing functionality.
    """
    password = "Password123"
    hashed = await get_password_hash_async(password)

    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password
    assert hashed.startswith("$2b$")
    assert len(hashed) > 50


def test_get_password_hash_fast() -> None:
    """
    Tests fast password hashing functionality.
    """
    password = "Password123"
    hashed = get_password_hash_fast(password)

    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password
    assert hashed.startswith("$2b$")
    assert len(hashed) > 50


@pytest.mark.asyncio
async def test_get_password_hash_fast_async() -> None:
    """
    Tests fast asynchronous password hashing functionality.
    """
    password = "Password123"
    hashed = await get_password_hash_fast_async(password)

    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password
    assert hashed.startswith("$2b$")
    assert len(hashed) > 50


# fmt: off
@pytest.mark.parametrize(
    "password, expected_result",
    verify_password_param_data,
    ids=["correct_password", "wrong_password", "empty_password"],
)
# fmt: on
def test_verify_password(password: str, expected_result: bool) -> None:
    """
Tests password verification with different scenarios.
"""
    hashed = get_password_hash_fast(password)
    assert verify_password(password, hashed) is expected_result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "hash_function, is_async",
    password_hashing_consistency_param_data,
    ids=["hash_async", "hash_fast", "hash_fast_async"],
)
async def test_password_hashing_consistency(hash_function: Callable[..., Any], is_async: bool) -> None:
    """
Tests consistency of different hashing functions.
"""
    password = "Password123"

    if is_async:
        func = await hash_function(password)
    else:
        func = hash_function(password)

    assert verify_password(password, func) is True
    assert verify_password("WrongPassword", func) is False


@pytest.mark.asyncio
async def test_password_hashing_uniqueness() -> None:
    """
Tests uniqueness of password hashes with same input.
"""
    password = "Password123"

    hash1 = await get_password_hash_async(password)
    hash2 = await get_password_hash_async(password)

    assert hash1 != hash2
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
