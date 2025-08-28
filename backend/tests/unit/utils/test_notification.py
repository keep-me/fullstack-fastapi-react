"""
Unit tests for notification utilities.
"""

from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock

import pytest

from app.models.schemas.user import UserPublic
from tests.parametrized_test_data import notification_sends_email_param_data


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "notification_func, email_data",
    notification_sends_email_param_data,
    ids=["signup_email", "password_changed_email", "delete_user_email", "password_reset_email"],
)
# fmt: on
async def test_notification_sends_email(
    notification_func: Callable[..., Any],
    email_data: dict[str, str | None],
    mock_rabbit_publish: AsyncMock,
    test_user_public: UserPublic,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
Tests that email notification is sent when TESTING is not set.
"""
    monkeypatch.delenv("TESTING", raising=False)

    if email_data["extra_data"] is not None:
        await notification_func(test_user_public, email_data["extra_data"])
    else:
        await notification_func(test_user_public)

    mock_rabbit_publish.assert_called_once()
    call_args, call_kwargs = mock_rabbit_publish.call_args
    sent_message = call_args[0]

    assert sent_message.to == test_user_public.email
    assert isinstance(sent_message.subject, str)
    assert sent_message.subject == email_data["subject"]
    assert sent_message.body == email_data["body"]
    if email_data["extra_data"] is not None:
        assert email_data["extra_data"] in sent_message.body
    assert call_kwargs.get("queue") == "email_queue"


# fmt: off
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "notification_func, email_data",
    notification_sends_email_param_data,
    ids=["signup_email", "password_changed_email", "delete_user_email", "password_reset_email"],
)
# fmt: on
async def test_notification_not_sent_in_test_mode(
    notification_func: Callable[..., Any],
    email_data: dict[str, str | None],
    mock_rabbit_publish: AsyncMock,
    test_user_public: UserPublic,
) -> None:
    """
Tests that email notification is NOT sent when TESTING is set.
"""

    if email_data["extra_data"] is not None:
        await notification_func(test_user_public, email_data["extra_data"])
    else:
        await notification_func(test_user_public)

    mock_rabbit_publish.assert_not_called()
