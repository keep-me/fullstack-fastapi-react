"""
Notification utilities.
"""

import os

from app.core.rabbit_mq import rabbit_router
from app.models.schemas.email import EmailMessage
from app.models.schemas.user import UserPublic


async def send_email(user: UserPublic, subject: str, body: str) -> None:
    """
    Send email message to user.
    """
    if (
        os.getenv("TESTING") == "1"
        or user.username.startswith("loaduser_")
        or user.username.startswith("playwright")
    ):
        return

    email_body = EmailMessage(
        to=user.email,
        subject=subject,
        body=body,
    )
    await rabbit_router.broker.publish(
        email_body,
        queue="email_queue",
    )


async def send_welcome_email(user: UserPublic) -> None:
    """
    Send welcome email to new user.
    """
    html_content = f"Hello, {user.username}! Welcome on a board!"
    await send_email(user, "Welcome!", html_content)


async def send_password_changed_email(user: UserPublic) -> None:
    """
    Send password change confirmation email.
    """
    html_content = (
        f"Hello, {user.username}! Your password has been changed successfully!"
    )
    await send_email(user, "Password changed successfully", html_content)


async def send_delete_user_email(user: UserPublic) -> None:
    """
    Send account deletion confirmation email.
    """
    html_content = (
        f"Hello, {user.username}! Your account has been deleted successfully!"
    )
    await send_email(user, "Account deleted successfully", html_content)


async def send_password_reset_email(user: UserPublic, verification_code: str) -> None:
    """
    Send password reset verification code email.
    """
    html_content = f"Hello, {user.username}! Please use the following code to reset your password: {verification_code}"
    await send_email(user, "Password reset", html_content)
