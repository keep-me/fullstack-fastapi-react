"""
Unit tests for user repository functionality.
"""

from typing import Any
from uuid import UUID

import pytest

from app.models.domain.user import User
from app.models.schemas.user import UserCreate, UserUpdate
from app.repositories.unit_of_work import UnitOfWork
from tests.parametrized_test_data import (
    repo_create_user_param_data,
    repo_get_by_user_id_param_data,
    repo_get_user_param_data,
    repo_get_users_pagination_param_data,
    repo_update_user,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_result",
    repo_get_by_user_id_param_data,
    ids=["existing_user", "non_existent_user"],
)
async def test_get_by_user_id(
    uow: UnitOfWork,
    mock_redis_client: Any,
    user_id: UUID,
    expected_result: Any,
) -> None:
    """
    Tests retrieving user by ID with caching.
    """
    user = await uow.users.get_by_user_id(session=uow.session, user_id=user_id)

    if not user:
        assert expected_result is False
    else:
        assert user.id == user_id

        cached_user = await uow.users.get_by_user_id(
            session=uow.session,
            user_id=user_id,
        )
        assert cached_user is not None
        assert cached_user.id == user_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field, value, expected_result",
    repo_get_user_param_data,
    ids=["by_username", "by_email", "not_found"],
)
async def test_get_user(
    uow: UnitOfWork,
    field: str,
    value: Any,
    expected_result: Any,
) -> None:
    """
    Tests retrieving user by different fields.
    """
    if isinstance(value, User):
        value = getattr(value, field)

    user = await uow.users.get_user(uow.session, **{field: value})

    if not user:
        assert expected_result is False
    else:
        assert getattr(user, field) == value


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, field, exception, expected_status_code, expected_message",
    repo_create_user_param_data,
    ids=["valid_user", "duplicate_username", "duplicate_email"],
)
# fmt: on
async def test_create_user(uow: UnitOfWork, test_user: User, user_data: dict[str, Any], field: str, exception: type[Exception] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests user creation with various scenarios.
"""
    if user_data.get(field):
        user_data[field] = getattr(test_user, field)

    user_create = UserCreate(**user_data)

    if not exception:
        user = await uow.users.create_user(uow.session, obj_in=user_create)
        assert user is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.full_name == user_data["full_name"]
        assert user.role.name == user_data["role"]
    else:
        with pytest.raises(exception) as exc:
            await uow.users.create_user(uow.session, obj_in=user_create)
        assert exc.value.status_code == expected_status_code # type: ignore[attr-defined]
        assert exc.value.message == expected_message # type: ignore[attr-defined]



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "new_data",
    repo_update_user,
    ids=["username", "email", "full_name"],
)
async def test_update_user(uow: UnitOfWork, test_user: User, new_data: dict[str, Any], mock_redis_client: Any) -> None:
    """
Tests updating user with different field combinations.
"""
    update_data = UserUpdate(**new_data)

    updated_user = await uow.users.update_user(
        session=uow.session, current_user=test_user, obj_in=update_data,
    )

    assert updated_user is not None
    assert updated_user.id == test_user.id
    assert updated_user.username == test_user.username
    for field, value in new_data.items():
        assert getattr(updated_user, field) == value

# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page, expected_counts",
    repo_get_users_pagination_param_data,
    ids=["first_page", "second_page", "last_page"],
)
# fmt: on
async def test_get_users_pagination(uow: UnitOfWork, random_user_data: dict[str, Any], page: dict[str, Any], expected_counts: int) -> None:
    """
Tests user pagination with different page parameters.
"""
    for i in range(5):
        user_data = UserCreate(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password="Password123",
            full_name=f"User {i}",
            role="USER",
        )
        await uow.users.create_user(uow.session, obj_in=user_data)

    users = await uow.users.get_users(uow.session, **page)
    assert len(users) == expected_counts

    if page["skip"] > 0:
        previous_page = await uow.users.get_users(
            uow.session, skip=page["skip"] - 2, limit=2,
        )
        assert users[0].id != previous_page[0].id
