"""
Lifespan event handlers.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.db import db_manager, init_db
from app.core.redis import redis_client


@retry(
    stop=stop_after_attempt(settings.DB_CONNECTION_RETRY_MAX_TRIES),
    wait=wait_fixed(settings.DB_CONNECTION_RETRY_WAIT_SECONDS),
)
async def check_db(session: AsyncSession) -> None:
    """
    Check Database Connection.
    """
    await session.execute(select(1))


async def init_data(session: AsyncSession) -> None:
    """
    Initialize Database Data.
    """
    await init_db(session)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan Event Handler.
    """
    session = db_manager.session_maker()
    try:
        await check_db(session)
        await redis_client.ping()
        await init_data(session)
        await session.commit()
        yield
    finally:
        await session.close()
        await redis_client.aclose()
        await db_manager.cleanup()
