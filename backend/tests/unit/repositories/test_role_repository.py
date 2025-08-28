"""
Unit tests for role repository functionality.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.domain.role import Role, RoleEnum
from app.models.schemas.role import RoleCreate
from app.repositories.role import RoleRepository
from tests.parametrized_test_data import (
    repo_create_new_role_param_data,
    repo_get_by_name_param_data,
    repo_get_or_create_param_data,
    repo_role_enum_param_data,
)


@pytest.fixture
def role_repository() -> RoleRepository:
    """
    Creates RoleRepository instance.
    """
    return RoleRepository()


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role_name, return_value, side_effect, test_case",
    repo_get_by_name_param_data,
    ids=["found", "not_found", "database_error"],
)
# fmt: on
async def test_get_by_name(role_repository: RoleRepository, mock_session: Any, role_name: RoleEnum, return_value: Any, side_effect: Any, test_case: str) -> None:
    """
Tests get_by_name method with various scenarios.
"""
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = return_value
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    if side_effect:
        mock_session.execute.side_effect = side_effect
    else:
        mock_session.execute.return_value = mock_result

    if side_effect:
        with pytest.raises(type(side_effect)):
            await role_repository.get_by_name(mock_session, role_name)
    else:
        result = await role_repository.get_by_name(mock_session, role_name)
        assert result == return_value

    mock_session.execute.assert_called_once()


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role_name, description, role_id, test_case",
    repo_create_new_role_param_data,
    ids=["without_id", "with_id"],
)
# fmt: on
async def test_create_new_role(role_repository: RoleRepository, mock_session: Any, role_name: RoleEnum, description: str, role_id: Any, test_case: str) -> None:
    """
Tests _create_new_role method with and without specific ID.
"""
    if role_id:
        mock_session.add = MagicMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()

        result = await role_repository._create_new_role(
            mock_session, role_name, description, role_id,
        )

        assert result.id == role_id
        assert result.name == role_name
        assert result.description == description
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()
    else:
        new_role = Role(id=2, name=role_name, description=description) # type: ignore[call-arg]

        with patch.object(role_repository, "create") as mock_create:
            mock_create.return_value = new_role

            result = await role_repository._create_new_role(
                mock_session, role_name, description,
            )

            assert result == new_role
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            assert call_args[1]["session"] == mock_session
            assert isinstance(call_args[1]["obj_in"], RoleCreate)
            assert call_args[1]["obj_in"].name == role_name
            assert call_args[1]["obj_in"].description == description


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role_name, description, role_id, existing_role, test_case",
    repo_get_or_create_param_data,
    ids=["existing_role", "new_role"],
)
# fmt: on
async def test_get_or_create(role_repository: RoleRepository, mock_session: Any, role_name: RoleEnum, description: str, role_id: Any, existing_role: Any, test_case: str) -> None:
    """
Tests get_or_create method for existing and new roles.
"""
    if existing_role:
        with patch.object(role_repository, "get_by_name") as mock_get:
            with patch.object(
                role_repository, "_update_role_description",
            ) as mock_update:
                mock_get.return_value = existing_role
                mock_update.return_value = existing_role

                result = await role_repository.get_or_create(
                    mock_session, role_name, description,
                )

                assert result == existing_role
                mock_get.assert_called_once_with(mock_session, role_name)
                mock_update.assert_called_once_with(
                    mock_session, existing_role, description,
                )
    else:
        new_role = Role(id=2, name=role_name, description=description) # type: ignore[call-arg]

        with patch.object(role_repository, "get_by_name") as mock_get:
            with patch.object(role_repository, "_create_new_role") as mock_create:
                mock_get.return_value = None
                mock_create.return_value = new_role

                result = await role_repository.get_or_create(
                    mock_session, role_name, description, role_id,
                )

                assert result == new_role
                mock_get.assert_called_once_with(mock_session, role_name)
                mock_create.assert_called_once_with(
                    mock_session, role_name, description, role_id,
                )


@pytest.mark.asyncio
async def test_initialize_roles(role_repository: RoleRepository, mock_session: Any) -> None:
    """
Tests initialization of all roles.
"""
    created_roles = [
        Role(id=1, name=RoleEnum.ADMIN, description="Administrator with full access"), # type: ignore[call-arg]
        Role(
            id=2,
            name=RoleEnum.MANAGER,
            description="Manager with limited administrative access",
        ), # type: ignore[call-arg]
        Role(id=3, name=RoleEnum.USER, description="Regular user"), # type: ignore[call-arg]
        Role(
            id=4, name=RoleEnum.GUEST, description="Guest user with restricted access", # type: ignore[call-arg]
        ),
    ]

    with patch.object(role_repository, "get_or_create") as mock_get_or_create:
        mock_get_or_create.side_effect = created_roles

        await role_repository.initialize_roles(mock_session)

        # assert mock_get_or_create.call_count == 4

        expected_calls = [
            (RoleEnum.ADMIN, "Administrator with full access", 1),
            (RoleEnum.MANAGER, "Manager with limited administrative access", 2),
            (RoleEnum.USER, "Regular user", 3),
            (RoleEnum.GUEST, "Guest user with restricted access", 4),
        ]

        for i, (expected_role, expected_desc, expected_id) in enumerate(expected_calls):
            call_args = mock_get_or_create.call_args_list[i]
            assert call_args[1]["session"] == mock_session
            assert call_args[1]["name"] == expected_role
            assert call_args[1]["description"] == expected_desc
            assert call_args[1]["role_id"] == expected_id


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role_enum, description",
    repo_role_enum_param_data,
    ids=["admin", "manager", "user", "guest"],
)
# fmt: on
async def test_get_by_name_with_different_roles(role_repository: RoleRepository, mock_session: Any, role_enum: RoleEnum, description: str) -> None:
    """
Tests get_by_name method with different role types.
"""
    mock_scalars = MagicMock()
    test_role = Role(id=1, name=role_enum, description=description) # type: ignore[call-arg]
    mock_scalars.first.return_value = test_role
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    result = await role_repository.get_by_name(mock_session, role_enum)

    assert result == test_role
    assert result.name == role_enum
    assert result.description == description


@pytest.mark.asyncio
async def test_update_role_description(role_repository: RoleRepository, mock_session: Any) -> None:
    """
Tests _update_role_description method.
"""
    existing_role = Role(id=1, name=RoleEnum.USER, description=None) # type: ignore[call-arg]
    description = "Updated description"

    with patch.object(role_repository, "update") as mock_update:
        updated_role = Role(id=1, name=RoleEnum.USER, description=description) # type: ignore[call-arg]
        mock_update.return_value = updated_role

        result = await role_repository._update_role_description(
            mock_session, existing_role, description,
        )

        assert result == updated_role
        mock_update.assert_called_once()

    existing_role_with_desc = Role(
        id=1, name=RoleEnum.USER, description="Existing description",
    ) # type: ignore[call-arg]

    with patch.object(role_repository, "update") as mock_update_no_call:
        result = await role_repository._update_role_description(
            mock_session, existing_role_with_desc, description,
        )

        assert result == existing_role_with_desc
        mock_update_no_call.assert_not_called()
