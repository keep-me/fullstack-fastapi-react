"""
Unit tests for response utilities.
"""

import json
from typing import Any
from unittest.mock import Mock

import pytest
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.utils.response import create_response
from tests.parametrized_test_data import (
    response_creation_param_data,
    response_request_id_priority_param_data,
    response_success_flag_based_on_status_code_param_data,
    response_with_request_id_param_data,
)


@pytest.mark.parametrize(
    "params, expected_response",
    response_creation_param_data,
    ids=["default_params", "with_data", "with_error"],
)
def test_response_creation(
    params: dict[str, Any],
    expected_response: dict[str, Any],
) -> None:
    """
    Tests response creation with different parameters.
    """
    response = create_response(**params)

    assert isinstance(response, JSONResponse)
    assert response.status_code == expected_response["status_code"]

    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["success"] == expected_response["success"]
    assert response_data["message"] == expected_response["message"]

    if expected_response["has_data"]:
        assert response_data["data"] == expected_response["data"]
    else:
        assert "data" not in response_data

    if expected_response["has_error"]:
        assert response_data["error"] == expected_response["error"]
    else:
        assert "error" not in response_data

    assert response_data["meta"]["request_id"] == expected_response["request_id"]


def test_response_with_custom_meta() -> None:
    """
    Tests response creation with custom metadata.
    """
    custom_meta: dict[str, Any] = {"page": 1, "limit": 10, "total": 100}
    response = create_response(meta=custom_meta)
    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["meta"]["page"] == 1
    assert response_data["meta"]["limit"] == 10
    assert response_data["meta"]["total"] == 100
    assert response_data["meta"]["request_id"] is None


@pytest.mark.parametrize(
    "request_id, expected_id",
    response_with_request_id_param_data,
    ids=["with_request_id", "without_request_id"],
)
def test_response_with_request_id(request_id: str, expected_id: str) -> None:
    """
    Tests response creation with and without request ID.
    """
    mock_request = Mock(spec=Request)
    mock_request.state = Mock()

    if request_id is not None:
        mock_request.state.request_id = request_id
    else:
        del mock_request.state.request_id

    response = create_response(request=mock_request)
    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["meta"]["request_id"] == expected_id


@pytest.mark.parametrize(
    "request_obj, meta_dict, expected_request_id",
    response_request_id_priority_param_data,
    ids=["meta_only", "request_overrides_meta"],
)
def test_response_request_id_priority(
    request_obj: Mock | None,
    meta_dict: dict[str, Any],
    expected_request_id: str,
) -> None:
    """
    Tests request ID priority in response creation.
    """
    response = create_response(request=request_obj, meta=meta_dict)
    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["meta"]["request_id"] == expected_request_id
    assert response_data["meta"]["other"] == "data"


# fmt: off
@pytest.mark.parametrize(
    "status_code, expected_response",
    response_success_flag_based_on_status_code_param_data,
    ids=["success_200", "success_201", "success_204", "failure_300", "failure_400", "failure_404", "failure_500"],
)
# fmt: on
def test_success_flag_based_on_status_code(
    status_code: int, expected_response: bool,
) -> None:
    """
Tests success flag setting based on status code.
"""
    response = create_response(status_code=status_code)
    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["success"] == expected_response
    assert response.status_code == status_code


def test_response_excludes_none_values() -> None:
    """
Tests exclusion of None values from response.
"""
    response = create_response(data=None, error=None)
    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert "data" not in response_data
    assert "error" not in response_data
    assert response_data["success"] is True
    assert response_data["message"] == "Success"


def test_response_with_complex_data_types() -> None:
    """
Tests response creation with complex data structures.
"""
    complex_data = {
        "users": [
            {"id": 1, "name": "John", "active": True},
            {"id": 2, "name": "Jane", "active": False},
        ],
        "metadata": {"count": 2, "filters": ["active", "name"]},
    }

    response = create_response(
        data=complex_data,
        status_code=status.HTTP_201_CREATED,
        message="Users created successfully",
    )

    assert response.status_code == status.HTTP_201_CREATED

    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["success"] is True
    assert response_data["data"] == complex_data
    assert response_data["message"] == "Users created successfully"


def test_response_with_all_parameters() -> None:
    """
Tests response creation with all available parameters.
"""
    mock_request = Mock(spec=Request)
    mock_request.state = Mock()
    mock_request.state.request_id = "full-test-request-id"

    test_data = {"result": "complete"}
    test_meta = {"version": "1.0", "timestamp": "2023-01-01"}

    response = create_response(
        data=test_data,
        message="Complete test",
        status_code=status.HTTP_201_CREATED,
        error=None,
        meta=test_meta,
        request=mock_request,
    )

    assert response.status_code == status.HTTP_201_CREATED

    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["success"] is True
    assert response_data["message"] == "Complete test"
    assert response_data["data"] == test_data
    assert response_data["meta"]["version"] == "1.0"
    assert response_data["meta"]["timestamp"] == "2023-01-01"
    assert response_data["meta"]["request_id"] == "full-test-request-id"


def test_request_id_conversion_to_string() -> None:
    """
Tests conversion of request ID to string format.
"""
    mock_request = Mock(spec=Request)
    mock_request.state = Mock()
    mock_request.state.request_id = 12345

    response = create_response(request=mock_request)
    content = bytes(response.body).decode()
    response_data = json.loads(content)

    assert response_data["meta"]["request_id"] == "12345"
    assert isinstance(response_data["meta"]["request_id"], str)
