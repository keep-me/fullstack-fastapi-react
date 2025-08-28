"""
RabbitMQ functionality.
"""

import asyncio
from email.mime.text import MIMEText

import aiosmtplib
from faststream.rabbit import RabbitQueue
from faststream.rabbit.fastapi import RabbitRouter

from app.core.config import settings
from app.models.schemas.email import EmailMessage

rabbit_router = RabbitRouter(
    url=f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/{settings.RABBITMQ_VHOST}",
    include_in_schema=True,
)

email_queue = RabbitQueue("email_queue", durable=True)


@rabbit_router.subscriber(email_queue)
async def handle_email_message(msg: EmailMessage) -> None:
    """
    Handle email message from RabbitMQ.
    """
    email = MIMEText(msg.body, "html")
    email["Subject"] = msg.subject
    email["From"] = settings.EMAIL_FROM
    email["To"] = msg.to

    await aiosmtplib.send(
        email,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        validate_certs=False,
    )


async def _run_rabbit_worker() -> None:
    """
    Run RabbitMQ worker in an event loop.
    """
    await rabbit_router.broker.connect()
    try:
        await rabbit_router.broker.start()
    finally:
        await rabbit_router.broker.close()


if __name__ == "__main__":
    asyncio.run(_run_rabbit_worker())
