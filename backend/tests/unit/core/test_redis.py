"""
Unit tests for Redis caching functionality.
"""

import pickle
from typing import Any
from uuid import UUID

import pytest
from redis.asyncio import Redis

from app.core.redis import get_redis
from app.models.domain.user import User
from app.models.schemas.user import UserCreate
from app.utils.cache import _generate_cache_key, cached
from tests.parametrized_test_data import redis_error_param_data


@pytest.mark.asyncio
async def test_get_redis_success() -> None:
    """
    Tests Redis client initialization and connection.
    """
    async for redis in get_redis():
        assert redis is not None
        assert isinstance(redis, Redis)
        await redis.ping()


@cached(ex=10)
async def cached_function(user_id: UUID) -> str | None:
    """
    A simple function to test the cache decorator.
    """
    if user_id is None:
        return None
    return f"processed-{user_id!s}"


@pytest.mark.asyncio
async def test_cache_decorator_cache_hit(
    mock_redis_client: Redis,
    test_user: User,
) -> None:
    """
    Tests cache decorator behavior on cache hit.
    """
    error_has_been_raised = False

    @cached(ex=10)
    async def _error_function(user_id: UUID) -> str:
        nonlocal error_has_been_raised
        error_has_been_raised = True
        raise ValueError("This function should not be called on a cache hit")

    expected_value = "this-is-a-cached-value"
    cache_key = await _generate_cache_key(test_user.id)
    await mock_redis_client.set(cache_key, pickle.dumps(expected_value))

    result = await _error_function(user_id=test_user.id)

    assert result == expected_value
    assert not error_has_been_raised


@pytest.mark.asyncio
async def test_cache_decorator_cache_miss(
    mock_redis_client: Redis,
    test_user: User,
) -> None:
    """
    Tests cache decorator behavior on cache miss.
    """
    expected_value = f"processed-{test_user.id!s}"
    cache_key = await _generate_cache_key(test_user.id)

    assert await mock_redis_client.get(cache_key) is None

    result = await cached_function(user_id=test_user.id)

    assert result == expected_value

    cached_value = await mock_redis_client.get(cache_key)
    assert cached_value is not None
    assert pickle.loads(cached_value) == expected_value


@pytest.mark.asyncio
async def test_cache_decorator_no_user_id() -> None:
    """
    Tests cache decorator behavior with no user ID.
    """
    result = await cached_function(user_id=None)
    assert result is None


@pytest.mark.asyncio
async def test_cache_decorator_ttl(mock_redis_client: Redis, test_user: User) -> None:
    """
    Tests cache decorator TTL setting.
    """
    expected_ttl = 10
    cache_key = await _generate_cache_key(test_user.id)

    await cached_function(user_id=test_user.id)

    ttl = await mock_redis_client.ttl(cache_key)
    assert 0 < ttl <= expected_ttl


@pytest.mark.asyncio
async def test_cache_with_different_params(
    mock_redis_client: Redis,
    test_user: User,
    uow: Any,
    random_user_data: dict[str, Any],
) -> None:
    """
    Tests cache behavior with different user IDs.
    """
    other_user = await uow.users.create_user(
        uow.session,
        obj_in=UserCreate(**random_user_data),
    )

    await cached_function(user_id=test_user.id)
    await cached_function(user_id=other_user.id)

    cache_key1 = await _generate_cache_key(test_user.id)
    cache_key2 = await _generate_cache_key(other_user.id)

    assert await mock_redis_client.exists(cache_key1)
    assert await mock_redis_client.exists(cache_key2)


@pytest.mark.asyncio
async def test_cache_expiration_is_set(
    mock_redis_client: Redis,
    test_user: User,
) -> None:
    """
    Tests cache expiration time setting.
    """

    @cached(ex=1)
    async def _short_expiry_function(user_id: UUID) -> str:
        return f"short-expiry-{user_id!s}"

    cache_key = await _generate_cache_key(test_user.id)
    expected_ttl = 1

    await _short_expiry_function(user_id=test_user.id)

    ttl = await mock_redis_client.ttl(cache_key)
    assert 0 < ttl <= expected_ttl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host, port, db, socket_timeout, exception",
    redis_error_param_data,
    ids=["invalid_host", "invalid_port", "invalid_db", "invalid_socket_timeout"],
)
async def test_redis_connection_error(
    host: str,
    port: int,
    db: int,
    socket_timeout: float,
    exception: type[Exception],
) -> None:
    """
    Tests Redis connection error handling.
    """
    client = Redis(
        host=host,
        port=port,
        db=db,
        encoding="utf-8",
        decode_responses=True,
        socket_timeout=socket_timeout,
        socket_connect_timeout=socket_timeout,
    )

    with pytest.raises(exception):
        await client.ping()
