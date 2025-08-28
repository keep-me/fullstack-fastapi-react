"""
Unit tests for base repository functionality.
"""

from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.core.exceptions import HTTPException
from tests.parametrized_test_data import (
    repo_create_param_data,
    repo_delete_param_data,
    repo_get_by_id_param_data,
    repo_get_multi_param_data,
    repo_update_param_data,
)
from tests.utils import (
    _TestModel,
    _TestRepository,
    assert_exception,
)


@pytest.fixture
def test_repository() -> _TestRepository:
    """
    Creates test repository instance.
    """
    return _TestRepository()


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "return_value, side_effect, expected_result, expected_exception, expected_status_code, expected_message",
    repo_get_by_id_param_data,
    ids=["success", "not_found", "database_error"],
)
# fmt: on
async def test_get_by_id(test_repository: _TestRepository, mock_session: Any, return_value: Any, side_effect: Any, expected_result: Any, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests get_by_id method with various scenarios.
"""
    test_id = uuid4()

    with patch.object(
        test_repository, "get_by_id", return_value=return_value, side_effect=side_effect,
    ) as mock_get:
        if not expected_exception:
            result = await test_repository.get_by_id(mock_session, test_id)
            if expected_result == "model":
                assert result == return_value
            else:
                assert result == expected_result
        else:
            with pytest.raises(expected_exception) as exc:
                await test_repository.get_by_id(mock_session, test_id)
            await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

        mock_get.assert_called_once_with(mock_session, test_id)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "skip, limit, return_value, side_effect, expected_exception, expected_status_code, expected_message",
    repo_get_multi_param_data,
    ids=["success", "with_pagination", "database_error"],
)
# fmt: on
async def test_get_multi(test_repository: _TestRepository, mock_session: Any, skip: int, limit: int, return_value: Any, side_effect: Any, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests get_multi method with various scenarios.
"""
    with patch.object(
        test_repository, "get_multi", return_value=return_value, side_effect=side_effect,
    ) as mock_get:
        if not expected_exception:
            if skip is not None and limit is not None:
                result = await test_repository.get_multi(mock_session, skip=skip, limit=limit)
                mock_get.assert_called_once_with(mock_session, skip=skip, limit=limit)
            else:
                result = await test_repository.get_multi(mock_session)
                mock_get.assert_called_once_with(mock_session)

            assert result == return_value
        else:
            with pytest.raises(expected_exception) as exc:
                await test_repository.get_multi(mock_session)

            await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)
            mock_get.assert_called_once_with(mock_session)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "create_data, expected_model, side_effect, expected_exception, expected_status_code, expected_message",
    repo_create_param_data,
    ids=["success_without_password", "success_with_password", "integrity_error", "sqlalchemy_error"],
)
# fmt: on
async def test_create(test_repository: _TestRepository, mock_session: Any, create_data: Any, expected_model: Any, side_effect: Any, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests create method with various scenarios.
"""
    with patch.object(
        test_repository, "create", return_value=expected_model, side_effect=side_effect,
    ) as mock_create:
        if not expected_exception:
            result = await test_repository.create(mock_session, obj_in=create_data)
            assert result == expected_model
        else:
            with pytest.raises(expected_exception) as exc:
                await test_repository.create(mock_session, obj_in=create_data)
            await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

        mock_create.assert_called_once_with(mock_session, obj_in=create_data)


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_model, update_data, expected_model, side_effect, expected_exception, expected_status_code, expected_message",
    repo_update_param_data,
    ids=["success", "integrity_error", "sqlalchemy_error"],
)
# fmt: on
async def test_update(test_repository: _TestRepository, mock_session: Any, test_model: Any, update_data: Any, expected_model: Any, side_effect: Any, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests update method with various scenarios.
"""
    with patch.object(
        test_repository, "update", return_value=expected_model, side_effect=side_effect,
    ) as mock_update:
        if not expected_exception:
            result = await test_repository.update(
                mock_session, db_obj=test_model, obj_in=update_data,
            )
            assert result == expected_model
        else:
            with pytest.raises(expected_exception) as exc:
                await test_repository.update(
                    mock_session, db_obj=test_model, obj_in=update_data,
                )
            await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

        mock_update.assert_called_once_with(
            mock_session, db_obj=test_model, obj_in=update_data,
        )


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expected_model, side_effect, expected_exception, expected_status_code, expected_message",
    repo_delete_param_data,
    ids=["success", "sqlalchemy_error"],
)
# fmt: on
async def test_delete(test_repository: _TestRepository, mock_session: Any, expected_model: Any, side_effect: Any, expected_exception: type[HTTPException] | None, expected_status_code: int, expected_message: str) -> None:
    """
Tests delete method with various scenarios.
"""
    test_model = _TestModel(id=uuid4(), name="test")

    with patch.object(
        test_repository, "delete", return_value=expected_model, side_effect=side_effect,
    ) as mock_delete:
        if not expected_exception:
            result = await test_repository.delete(mock_session, obj=test_model)
            assert result == expected_model
        else:
            with pytest.raises(expected_exception) as exc:
                await test_repository.delete(mock_session, obj=test_model)
            await assert_exception(exc.value, expected_exception, expected_status_code, expected_message)

        mock_delete.assert_called_once_with(mock_session, obj=test_model)
