"""
Unit tests for session repository functionality.
"""

import pytest

from app.models.domain.user import User
from app.repositories.unit_of_work import UnitOfWork
from tests.parametrized_test_data import (
    get_by_refresh_token_param_data,
    remove_session_param_data,
)
from tests.utils import (
    assert_session_matches,
    create_test_refresh_token,
    create_test_session,
)


@pytest.mark.asyncio
async def test_create_session(uow: UnitOfWork, test_user: User) -> None:
    """
    Tests session creation functionality.
    """
    fingerprint = "test-fingerprint"
    refresh_token = create_test_refresh_token(test_user.id)

    session = await uow.sessions.create_or_update_session(
        uow.session,
        test_user.id,
        refresh_token,
        fingerprint,
    )

    assert_session_matches(session, test_user.id, refresh_token, fingerprint)


@pytest.mark.asyncio
async def test_update_session(uow: UnitOfWork, test_user: User) -> None:
    """
    Tests session update functionality.
    """
    initial_session, refresh_token1, fingerprint = await create_test_session(
        uow.session,
        test_user.id,
    )
    refresh_token2 = create_test_refresh_token(test_user.id)

    updated_session = await uow.sessions.create_or_update_session(
        uow.session,
        test_user.id,
        refresh_token2,
        fingerprint,
    )

    assert updated_session is not None
    assert updated_session.id == initial_session.id
    assert_session_matches(updated_session, test_user.id, refresh_token2, fingerprint)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "refresh_token, expected_result",
    get_by_refresh_token_param_data,
    ids=["non_existing_token", "existing_token"],
)
# fmt: on
async def test_get_by_refresh_token(uow: UnitOfWork, test_user: User, refresh_token: str, expected_result: str | None) -> None:
    """
Tests retrieving session by refresh token.
"""
    if not refresh_token:
        session, refresh_token, fingerprint = await create_test_session(
            uow.session, test_user.id,
        )
        expected_result = refresh_token
        expected_user_id = test_user.id
        expected_fingerprint = fingerprint

    session = await uow.sessions.get_by_refresh_token(uow.session, refresh_token)

    if not session:
        assert expected_result is None
    else:
        assert_session_matches(
            session, expected_user_id, refresh_token, expected_fingerprint,
        )

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "refresh_token, expected_result",
    remove_session_param_data,
    ids=["non_existing_token", "existing_token"],
)
# fmt: on
async def test_remove_session(uow: UnitOfWork, test_user: User, refresh_token: str, expected_result: bool) -> None:
    """
Tests session removal functionality.
"""
    if not refresh_token:
        _, refresh_token, _ = await create_test_session(uow.session, test_user.id)

    result = await uow.sessions.delete_by_refresh_token(uow.session, refresh_token)
    assert result is expected_result

    deleted_session = await uow.sessions.get_by_refresh_token(uow.session, refresh_token)
    assert deleted_session is None
