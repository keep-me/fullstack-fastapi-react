"""
Unit tests for RabbitMQ message handling functionality.
"""

from unittest.mock import AsyncMock, patch

import pytest
from aiosmtplib.errors import SMTPException

from app.core.rabbit_mq import (
    _run_rabbit_worker,
    handle_email_message,
)
from app.models.schemas.email import EmailMessage


@pytest.mark.asyncio
async def test_handle_email_message_success() -> None:
    """
    Tests successful email message handling.
    """
    email_msg = EmailMessage(
        to="test@example.com",
        subject="Test Subject",
        body="<p>Test Body</p>",
    )

    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        await handle_email_message(email_msg)

        mock_send.assert_awaited_once()
        sent_email = mock_send.call_args[0][0]
        assert sent_email["To"] == email_msg.to
        assert sent_email["Subject"] == email_msg.subject
        assert sent_email.get_payload() == email_msg.body


@pytest.mark.asyncio
async def test_handle_email_message_smtp_failure() -> None:
    """
    Tests email message handling with SMTP failure.
    """
    email_msg = EmailMessage(
        to="test@example.com",
        subject="Test Subject",
        body="<p>Test Body</p>",
    )

    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = SMTPException("Test SMTP Error")
        with pytest.raises(SMTPException):
            await handle_email_message(email_msg)


@pytest.mark.asyncio
async def test_run_rabbit_worker() -> None:
    """
    Tests RabbitMQ worker lifecycle management.
    """
    with patch(
        "app.core.rabbit_mq.rabbit_router.broker",
        new_callable=AsyncMock,
    ) as mock_broker:
        await _run_rabbit_worker()

        mock_broker.connect.assert_awaited_once()
        mock_broker.start.assert_awaited_once()
        mock_broker.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_rabbit_worker_closes_on_error() -> None:
    """
    Tests RabbitMQ worker cleanup on error.
    """
    with patch(
        "app.core.rabbit_mq.rabbit_router.broker",
        new_callable=AsyncMock,
    ) as mock_broker:
        mock_broker.start.side_effect = ValueError("Test Exception")

        with pytest.raises(ValueError, match="Test Exception"):
            await _run_rabbit_worker()

        mock_broker.connect.assert_awaited_once()
        mock_broker.start.assert_awaited_once()
        mock_broker.close.assert_awaited_once()
