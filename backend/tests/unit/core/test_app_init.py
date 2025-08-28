"""
Unit tests for database initialization and application lifecycle.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import DatabaseManager, db_manager, init_db
from app.core.events import check_db, init_data, lifespan
from app.core.exceptions import DatabaseError
from app.models.domain.user import User
from app.repositories.user import user_repo


def test_singleton_pattern() -> None:
    """
    Tests that DatabaseManager implements the Singleton pattern.
    """

    instance1 = DatabaseManager()
    instance2 = DatabaseManager()
    assert instance1 is instance2
    assert instance1 is db_manager


@pytest.mark.asyncio
async def test_cleanup() -> None:
    """
    Tests that the cleanup method correctly resets the state.
    """
    manager = DatabaseManager()

    assert manager.session_maker is not None
    assert manager._engine is not None

    await manager.cleanup()
    assert manager._engine is None
    assert manager._session_maker is None

    new_session_maker = manager.session_maker
    assert new_session_maker is not None
    assert manager._engine is not None


@pytest.mark.asyncio
async def test_init_db_creates_superuser(db_session: AsyncSession) -> None:
    """
    Tests that init_db correctly creates a superuser.
    """

    existing_user = await user_repo.get_user(
        session=db_session,
        username=settings.FIRST_SUPERUSER_USERNAME,
    )
    if existing_user:
        await db_session.delete(existing_user)
        await db_session.commit()

    user = await init_db(db_session)
    await db_session.commit()

    assert user is not None
    assert user.username == settings.FIRST_SUPERUSER_USERNAME
    assert user.is_admin is True

    await db_session.delete(user)
    await db_session.commit()


@pytest.mark.asyncio
async def test_init_db_superuser_already_exists(db_session: AsyncSession) -> None:
    """
    Tests that init_db does not create a duplicate superuser.
    """
    initial_user = await init_db(db_session)
    await db_session.commit()
    assert initial_user is not None

    second_run_user = await init_db(db_session)
    await db_session.commit()

    assert second_run_user is not None
    assert second_run_user.id == initial_user.id

    query = select(func.count(User.id)).where(
        User.username == settings.FIRST_SUPERUSER_USERNAME,
    )
    count = (await db_session.execute(query)).scalar_one()
    assert count == 1

    await db_session.delete(initial_user)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected_error, expected_message",
    [
        (SQLAlchemyError("DB Error"), "DB Error"),
        (Exception("Generic Error"), "Unable to connect to database"),
    ],
    ids=["sqlalchemy_error", "general_error"],
)
async def test_init_db_error_handling(
    mock_session: MagicMock,
    expected_error: Exception,
    expected_message: str,
) -> None:
    """
    Tests that the error handling for database initialization is correct.
    """
    with patch("app.repositories.role.role_repo.initialize_roles") as mock_init_roles:
        mock_init_roles.side_effect = expected_error

        with pytest.raises(DatabaseError) as exc_info:
            await init_db(mock_session)

        assert exc_info.value.error == expected_message


@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_check_db_with_retries(mock_sleep: AsyncMock) -> None:
    """
    Tests that check_db performs retries on failure.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.execute.side_effect = [
        SQLAlchemyError("Connection failed"),
        SQLAlchemyError("Connection failed again"),
        MagicMock(),
    ]

    await check_db(mock_session)

    assert mock_session.execute.call_count == 3
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
@patch("app.core.events.init_db", new_callable=AsyncMock)
async def test_init_data(mock_init_db: AsyncMock) -> None:
    """
    Tests that init_data calls init_db.
    """
    mock_session = AsyncMock()
    await init_data(mock_session)
    mock_init_db.assert_awaited_once_with(mock_session)


@pytest.mark.asyncio
@patch("app.core.events.db_manager")
@patch("app.core.events.redis_client")
@patch("app.core.events.check_db", new_callable=AsyncMock)
@patch("app.core.events.init_data", new_callable=AsyncMock)
async def test_lifespan_handler_success(
    mock_init_data: AsyncMock,
    mock_check_db: AsyncMock,
    mock_redis_client: MagicMock,
    mock_db_manager: MagicMock,
) -> None:
    """
    Tests that the lifespan handler correctly performs all steps when starting and stopping the application.
    """
    mock_app = MagicMock()
    mock_session = AsyncMock()
    mock_db_manager.session_maker.return_value = mock_session
    mock_redis_client.ping = AsyncMock()
    mock_redis_client.aclose = AsyncMock()
    mock_db_manager.cleanup = AsyncMock()

    async with lifespan(mock_app):
        pass

    mock_db_manager.session_maker.assert_called_once()
    mock_check_db.assert_awaited_once_with(mock_session)
    mock_redis_client.ping.assert_awaited_once()
    mock_init_data.assert_awaited_once_with(mock_session)
    mock_session.commit.assert_awaited_once()

    mock_session.close.assert_awaited_once()
    mock_redis_client.aclose.assert_awaited_once()
    mock_db_manager.cleanup.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.core.events.db_manager")
@patch("app.core.events.redis_client")
@patch("app.core.events.check_db", new_callable=AsyncMock)
async def test_lifespan_handler_failure(
    mock_check_db: AsyncMock,
    mock_redis_client: MagicMock,
    mock_db_manager: MagicMock,
) -> None:
    """
    Tests that the lifespan handler correctly closes resources on failure.
    """
    mock_app = MagicMock()
    mock_session = AsyncMock()
    mock_db_manager.session_maker.return_value = mock_session
    mock_check_db.side_effect = Exception("Test error")
    mock_redis_client.aclose = AsyncMock()
    mock_db_manager.cleanup = AsyncMock()

    with pytest.raises(Exception, match="Test error"):
        async with lifespan(mock_app):
            pass

    mock_session.close.assert_awaited_once()
    mock_redis_client.aclose.assert_awaited_once()
    mock_db_manager.cleanup.assert_awaited_once()
