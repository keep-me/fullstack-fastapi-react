"""
Unit tests for user service functionality.
"""

from typing import Any

import pytest

from app.core.exceptions import HTTPException
from app.models.schemas.user import UpdatePassword, UserCreate, UserPublic, UserUpdate
from app.repositories.unit_of_work import UnitOfWork
from app.services.user_service import UserService
from app.utils.password import verify_password
from tests.parametrized_test_data import (
    user_service_create_user_param_data,
    user_service_delete_user_by_id_param_data,
    user_service_delete_user_me_param_data,
    user_service_get_user_by_id_param_data,
    user_service_update_password_me_param_data,
    user_service_update_user_by_id_param_data,
    user_service_update_user_me_param_data,
)
from tests.utils import assert_exception


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_in_data, expected_exception, expected_status_code, expected_message",
    user_service_create_user_param_data,
    ids=["success", "username_exists", "empty_username", "email_exists", "empty_email", "invalid_email", "empty_password"],
)
# fmt: on
async def test_create_user(
    uow: UnitOfWork,
    request: Any,
    user_in_data: dict[str, Any],
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    random_user_data: dict[str, Any],
    mock_redis_client: Any,
) -> None:
    """
Tests user creation with various input scenarios.
"""
    user_service = UserService(uow)

    if isinstance(user_in_data, dict):
        random_user_data.update(user_in_data)

    if not expected_exception:
        user = await user_service.create_user(UserCreate(**random_user_data))
        assert isinstance(user, UserPublic)
        assert user.username == random_user_data["username"]
    else:
        with pytest.raises(expected_exception) as exc:
            await user_service.create_user(UserCreate(**random_user_data))
        await assert_exception(
            exc.value, expected_exception, expected_status_code, expected_message,
        )


@pytest.mark.asyncio
async def test_get_users(uow: UnitOfWork, test_user: Any, test_superuser: Any, mock_redis_client: Any) -> None:
    """
Tests retrieving list of users with pagination.
"""
    user_service = UserService(uow)
    users = await user_service.get_users(skip=0, limit=10)
    assert isinstance(users, list)
    assert len(users) >= 2
    assert all(isinstance(u, UserPublic) for u in users)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_user_data, expected_exception, expected_status_code, expected_message",
    user_service_update_user_me_param_data,
    ids=["new_username_valid", "new_username_exists", "new_username_empty", "new_email_valid", "new_email_exists", "new_email_empty", "new_email_invalid", "new_fullname_valid", "new_full_name_empty", "empty_data"],
)
# fmt: on
async def test_update_user_me(
    uow: UnitOfWork,
    test_user: Any,
    update_user_data: dict[str, Any],
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests self-update functionality for user profile.
"""
    user_service = UserService(uow)

    if not expected_exception:
        updated_user = await user_service.update_user_me(test_user, UserUpdate(**update_user_data))
        assert set(["id", "username", "email", "full_name", "is_active", "role"]).issubset(updated_user.model_dump())
    else:
        with pytest.raises(expected_exception) as exc:
            await user_service.update_user_me(test_user, UserUpdate(**update_user_data))
        await assert_exception(
            exc.value, expected_exception, expected_status_code, expected_message,
        )

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "current_password, new_password, expected_exception, expected_status_code, expected_message",
    user_service_update_password_me_param_data,
    ids=["success", "incorrect_current", "same_password", "empty_current_password", "empty_new_password"],
)
# fmt: on
async def test_update_password_me(
    uow: UnitOfWork,
    test_user: Any,
    current_password: str,
    new_password: str,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests self-update functionality for user password.
"""
    user_service = UserService(uow)

    if not expected_exception:
        await user_service.update_password_me(test_user, UpdatePassword(
        current_password=current_password, new_password=new_password,
    ))

        refreshed_user = await uow.users.get_by_id(uow.session, test_user.id)
        assert refreshed_user is not None
        assert verify_password(new_password, refreshed_user.hashed_password)
    else:
        with pytest.raises(expected_exception) as exc:
            await user_service.update_password_me(test_user, UpdatePassword(
        current_password=current_password, new_password=new_password,
    ))
        await assert_exception(
            exc.value, expected_exception, expected_status_code, expected_message,
        )

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user, expected_exception, expected_status_code, expected_message",
    user_service_delete_user_me_param_data,
    ids=["success", "self_delete_admin"],
)
# fmt: on
async def test_delete_user_me(
    uow: UnitOfWork,
    user: Any,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests self-deletion functionality for user account.
"""
    user_service = UserService(uow)

    if not expected_exception:
        await user_service.delete_user_me(user)
        deleted_user = await uow.users.get_by_id(uow.session, user.id)
        assert deleted_user is not None
        assert deleted_user.is_active is False
    else:
        with pytest.raises(expected_exception) as exc:
            await user_service.delete_user_me(user)
        await assert_exception(
            exc.value, expected_exception, expected_status_code, expected_message,
        )

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_exception, expected_status_code, expected_message",
    user_service_get_user_by_id_param_data,
    ids=["success", "not_found"],
)
# fmt: on
async def test_get_user_by_id(
    uow: UnitOfWork,
    user_id: Any,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests retrieving user by ID functionality.
"""
    user_service = UserService(uow)
    if not expected_exception:
        user = await user_service.get_user_by_id(user_id)
        assert user is not None
        assert str(user.id) == str(user_id)
    else:
        with pytest.raises(expected_exception) as exc:
            await user_service.get_user_by_id(user_id)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, update_data, expected_exception, expected_status_code, expected_message",
    user_service_update_user_by_id_param_data,
    ids=["update_username", "update_email", "update_password", "user_not_found", "username_exists", "email_exists", "invalid_email", "empty_email", "empty_data", "full_name_empty", "is_active_false", "is_active_true", "role_user", "role_admin", "password_empty", "password_same_as_current"],
)
# fmt: on
async def test_update_user_by_id(
    uow: UnitOfWork,
    test_superuser: Any,
    user_id: Any,
    update_data: dict[str, Any],
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests updating user by ID functionality.
"""
    user_service = UserService(uow)

    if not expected_exception:
        updated_user = await user_service.update_user(test_superuser, user_id, UserUpdate(**update_data))
        assert isinstance(updated_user, UserPublic)
    else:
        with pytest.raises(expected_exception) as exc:
            await user_service.update_user(test_superuser, user_id, UserUpdate(**update_data))
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_exception, expected_status_code, expected_message",
    user_service_delete_user_by_id_param_data,
    ids=["success", "user_not_found"],
)
# fmt: on
async def test_delete_user_by_id(
    uow: UnitOfWork,
    user_id: Any,
    expected_exception: type[HTTPException] | None,
    expected_status_code: int,
    expected_message: str,
    mock_redis_client: Any,
) -> None:
    """
Tests deleting user by ID functionality.
"""
    user_service = UserService(uow)

    if not expected_exception:
        deleted_user = await user_service.delete_user_by_id(user_id)
        assert isinstance(deleted_user, UserPublic)

        db_user = await uow.users.get_by_user_id(uow.session, user_id)
        assert db_user is not None
        assert db_user.is_active is False
    else:
        with pytest.raises(expected_exception) as exc:
            await user_service.delete_user_by_id(user_id)
        await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)
