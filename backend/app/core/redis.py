"""
Redis functionality.
"""

from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings


class RedisClientFactory:
    """
    Factory for creating Redis clients with different configurations.
    """

    @staticmethod
    def create_default_client() -> Redis:
        """
        Create default Redis client with settings from config.
        """
        return Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            encoding="utf-8",
            decode_responses=False,
            socket_timeout=settings.REDIS_TIMEOUT,
            max_connections=20,
            retry_on_timeout=True,
        )


redis_client = RedisClientFactory.create_default_client()


async def get_redis() -> AsyncGenerator[Redis]:
    """
    Redis dependency.
    """
    try:
        await redis_client.ping()
        yield redis_client
    finally:
        pass
