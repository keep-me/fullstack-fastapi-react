"""
Cache utilities for the application.
"""

import functools
import pickle
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar
from uuid import UUID

from app.core.redis import redis_client

T = TypeVar("T")
P = TypeVar("P")


async def _generate_cache_key(user_id: UUID) -> str:
    """
    Generate a cache key for a user ID.
    """
    return f"user:id:{user_id!s}"


async def _invalidate_user_cache(user_id: UUID) -> None:
    """
    Invalidate the cache for a user using the global redis_client.
    """
    cache_key = await _generate_cache_key(user_id)
    await redis_client.delete(cache_key)


def invalidate_cache() -> Callable[
    [Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]
]:
    """
    Decorator to invalidate user cache after a method is executed.
    """

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = await func(*args, **kwargs)

            if result and hasattr(result, "id"):
                await _invalidate_user_cache(result.id)

            return result

        return wrapper

    return decorator


def cached(
    ex: int = 60,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Decorator to cache function results in Redis.
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            user_id = kwargs.get("user_id")
            if not user_id:
                result = await func(*args, **kwargs)
                return result

            cache_key = await _generate_cache_key(user_id)

            data = await redis_client.get(cache_key)
            if data:
                cached_result: T = pickle.loads(data)
                return cached_result

            result = await func(*args, **kwargs)
            if result is not None:
                await redis_client.set(cache_key, pickle.dumps(result), ex=ex)
            return result

        return wrapper

    return decorator
