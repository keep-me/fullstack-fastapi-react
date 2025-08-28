"""
Fixtures for unit and performance tests.
"""

import os

os.environ["TESTING"] = "1"
os.environ["ENVIRONMENT"] = "local"

import random
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from fakeredis import FakeAsyncRedis
from fastapi import status
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.config import settings
from app.core.db import db_manager, get_session
from app.core.rabbit_mq import rabbit_router
from app.core.redis import get_redis
from app.main import app
from app.models.base import Base
from app.models.domain.role import RoleEnum
from app.models.domain.user import User
from app.models.schemas.user import UserPublic
from app.repositories.role import role_repo
from app.repositories.unit_of_work import UnitOfWork
from app.repositories.user import user_repo
from app.utils.password import get_password_hash_fast_async


def get_test_database_url(worker_id: str | None = None) -> str:
    """
    Generate unique database URL for each pytest-xdist worker.
    """
    test_database_url = settings.TEST_DATABASE_URL

    if test_database_url.startswith("sqlite"):
        return test_database_url

    if worker_id is None or worker_id == "master":
        return test_database_url

    base_url, db_name = test_database_url.rsplit("/", 1)
    worker_db_name = f"{db_name}_{worker_id}"
    return f"{base_url}/{worker_db_name}"


async def _create_worker_database(test_db_url: str) -> None:
    """
    Create a unique database for a pytest-xdist worker.
    """
    db_name = test_db_url.rsplit("/", 1)[1]
    admin_url = test_db_url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_async_engine(
        admin_url, echo=False, isolation_level="AUTOCOMMIT"
    )

    try:
        async with admin_engine.begin() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            await conn.execute(text(f"CREATE DATABASE {db_name}"))
    finally:
        await admin_engine.dispose()


async def _drop_worker_database(test_db_url: str) -> None:
    """
    Drop the unique database for a pytest-xdist worker.
    """
    db_name = test_db_url.rsplit("/", 1)[1]
    admin_url = test_db_url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_async_engine(
        admin_url, echo=False, isolation_level="AUTOCOMMIT"
    )

    try:
        async with admin_engine.begin() as conn:
            await conn.execute(
                text(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{db_name}' AND pid <> pg_backend_pid()""")
            )
            await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
    finally:
        await admin_engine.dispose()


@pytest.fixture(scope="session")
def worker_id(request: pytest.FixtureRequest) -> Any:
    """
    Get the worker ID for pytest-xdist.
    """
    return getattr(request.config, "workerinput", {}).get("workerid", None)


@pytest_asyncio.fixture(scope="function")
async def engine(worker_id: str | None) -> AsyncGenerator[AsyncEngine]:
    """
    Provides a database engine instance.
    """
    test_db_url = get_test_database_url(worker_id)
    engine = create_async_engine(test_db_url, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def setup_db(engine: AsyncEngine, worker_id: str | None) -> AsyncGenerator[None]:
    """
    Sets up the database schema.
    """
    test_db_url = get_test_database_url(worker_id)

    if (
        test_db_url.startswith("postgresql")
        and worker_id is not None
        and worker_id != "master"
    ):
        await _create_worker_database(test_db_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        await role_repo.initialize_roles(session)
        await session.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    if (
        test_db_url.startswith("postgresql")
        and worker_id is not None
        and worker_id != "master"
    ):
        await _drop_worker_database(test_db_url)


@pytest_asyncio.fixture(scope="function")
async def db_session(
    setup_db: Any,
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession]:
    """
    Provides a database session.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
def mock_session() -> AsyncMock:
    """
    Provides a mock database session.
    """
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture(scope="function")
async def uow(db_session: AsyncSession) -> AsyncGenerator[UnitOfWork]:
    """
    Provides a Unit of Work instance.
    """
    async with UnitOfWork(db_session) as uow:
        yield uow


@pytest.fixture
def mock_send_email(monkeypatch: Any) -> AsyncMock:
    """
    Provides a mock for email sending functions.
    """
    mock = AsyncMock()
    monkeypatch.setattr("app.services.auth_service.send_welcome_email", mock)
    monkeypatch.setattr("app.services.auth_service.send_password_reset_email", mock)
    monkeypatch.setattr("app.api.endpoints.users.send_welcome_email", mock)
    monkeypatch.setattr("app.api.endpoints.users.send_password_changed_email", mock)
    monkeypatch.setattr("app.api.endpoints.users.send_delete_user_email", mock)
    return mock


@pytest.fixture(scope="function")
def mock_rabbit_publish() -> Generator[AsyncMock, None, None]:
    """
    Provides a session-scoped mock for the RabbitMQ publish method.
    """
    mock = AsyncMock()
    with patch("app.utils.notification.rabbit_router.broker.publish", new=mock):
        yield mock


@pytest_asyncio.fixture(scope="function")
async def test_user(
    db_session: AsyncSession,
    mock_send_email: Any,
) -> AsyncGenerator[User]:
    """
    Creates and provides a test user.
    """
    role = await role_repo.get_or_create(
        session=db_session,
        name=RoleEnum.USER,
        description="Regular user",
    )

    user = User(
        username="testuser",
        full_name="Test User",
        email="testuser@example.com",
        hashed_password=await get_password_hash_fast_async("Password123"),
        is_active=True,
    )  # type: ignore[call-arg]

    user.role = role
    db_session.add(user)
    await db_session.commit()

    yield user


@pytest_asyncio.fixture(scope="function")
async def test_superuser(
    db_session: AsyncSession,
    mock_send_email: Any,
) -> AsyncGenerator[User]:
    """
    Creates and provides a test superuser.
    """
    role = await role_repo.get_or_create(
        session=db_session,
        name=RoleEnum.ADMIN,
        description="Administrator",
    )

    user = User(
        username="admin",
        full_name="Test Admin",
        email="admin@example.com",
        hashed_password=await get_password_hash_fast_async("Password123"),
        is_active=True,
    )  # type: ignore[call-arg]

    user.role = role
    db_session.add(user)
    await db_session.commit()

    yield user


@pytest.fixture
def test_user_public() -> UserPublic:
    """
    Provides a test UserPublic object.
    """
    return UserPublic(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        role=RoleEnum.USER,
    )


@pytest.fixture(scope="function")
def random_user_data() -> dict[str, Any]:
    """
    Generates random user data.
    """
    suffix = random.randint(1, 99999)
    return {
        "username": f"randomuser_{suffix}",
        "email": f"randomuser_{suffix}@example.com",
        "password": "Password123",
        "full_name": f"Random User {suffix}",
        "role": RoleEnum.USER,
        "is_active": True,
    }


@pytest_asyncio.fixture(scope="function")
async def redis_client() -> AsyncGenerator[Redis]:
    """
    Provides a Redis client instance.
    """
    redis = FakeAsyncRedis(decode_responses=False)
    try:
        yield redis
    finally:
        await redis.flushall()
        await redis.aclose()


@pytest.fixture(scope="function")
def mock_redis_client(monkeypatch: Any, redis_client: Redis) -> Redis:
    """
    Provides a mock Redis client.
    """
    monkeypatch.setattr("app.core.redis.redis_client", redis_client)
    monkeypatch.setattr("app.utils.cache.redis_client", redis_client)
    monkeypatch.setattr("app.utils.auth.redis_client", redis_client)
    monkeypatch.setattr("app.services.auth_service.redis_client", redis_client)
    return redis_client


@pytest_asyncio.fixture(scope="function")
async def async_client(
    db_session: AsyncSession,
    mock_redis_client: Redis,
) -> AsyncGenerator[AsyncClient]:
    """
    Provides an async HTTP client.
    """

    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        try:
            yield db_session
            await db_session.commit()
        except SQLAlchemyError:
            await db_session.rollback()
            raise
        finally:
            await db_session.close()

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id(test_user: User) -> Any:
    """
    Provides test user ID.
    """
    return test_user.id


@pytest.fixture
def test_user_username(test_user: User) -> str:
    """
    Provides test user username.
    """
    return test_user.username


@pytest.fixture
def test_user_email(test_user: User) -> str:
    """
    Provides test user email.
    """
    return test_user.email


@pytest.fixture
def test_user_full_name(test_user: User) -> str:
    """
    Provides test user full name.
    """
    return test_user.full_name or ""


@pytest_asyncio.fixture
async def test_user_username_inactive(db_session: AsyncSession, test_user: User) -> str:
    """
    Provides inactive test user username.
    """
    test_user.is_active = False
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user.username


@pytest_asyncio.fixture
async def test_user_email_inactive(db_session: AsyncSession, test_user: User) -> str:
    """
    Provides inactive test user email.
    """
    test_user.is_active = False
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user.email


@pytest_asyncio.fixture
async def test_user_id_inactive(db_session: AsyncSession, test_user: User) -> Any:
    """
    Provides inactive test user ID.
    """
    test_user.is_active = False
    await db_session.commit()
    await db_session.refresh(test_user)
    return test_user.id


@pytest.fixture
def test_superuser_id(test_superuser: User) -> Any:
    """
    Provides test superuser ID.
    """
    return test_superuser.id


@pytest.fixture
def test_superuser_username(test_superuser: User) -> str:
    """
    Provides test superuser username.
    """
    return test_superuser.username


@pytest.fixture
def test_superuser_email(test_superuser: User) -> str:
    """
    Provides test superuser email.
    """
    return test_superuser.email


@pytest_asyncio.fixture
async def login_and_get_headers_test_user(
    async_client: AsyncClient,
    test_user: User,
) -> dict[str, str]:
    """
    Provides authorization headers for test user.
    """
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "Password123",
            "fingerprint": "test_fingerprint",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    async_client.cookies.set(
        settings.REFRESH_TOKEN_COOKIES_NAME, tokens["refresh_token"]
    )
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest_asyncio.fixture
async def login_and_get_headers_test_superuser(
    async_client: AsyncClient,
    test_superuser: User,
) -> dict[str, str]:
    """
    Provides authorization headers for test superuser.
    """
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": test_superuser.username,
            "password": "Password123",
            "fingerprint": "test_fingerprint",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    async_client.cookies.set(
        settings.REFRESH_TOKEN_COOKIES_NAME, tokens["refresh_token"]
    )
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def perf_redis_client() -> AsyncGenerator[Redis]:
    """
    Provides Redis client for performance tests.
    """
    redis = FakeAsyncRedis(decode_responses=False)
    try:
        yield redis
    finally:
        await redis.flushall()
        await redis.aclose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def perf_uow() -> AsyncGenerator[UnitOfWork]:
    """
    Provides Unit of Work for performance tests.
    """
    async with db_manager.session_maker() as session:
        uow = UnitOfWork(session)
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise
        finally:
            await uow.session.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def perf_client(perf_redis_client: Redis) -> AsyncGenerator[AsyncClient]:
    """
    Provides HTTP client for performance tests.
    """

    async def mock_rabbit_publish(*args: Any, **kwargs: Any) -> None:
        """
        Mock for RabbitMQ publish.
        """

    app.dependency_overrides[get_redis] = lambda: perf_redis_client

    original_publish = rabbit_router.broker.publish
    setattr(rabbit_router.broker, "publish", mock_rabbit_publish)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    setattr(rabbit_router.broker, "publish", original_publish)
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def perf_test_user(perf_uow: UnitOfWork) -> AsyncGenerator[User, None]:
    """
    Creates test user for performance tests.
    """
    role = await role_repo.get_or_create(
        session=perf_uow.session,
        name=RoleEnum.USER,
        description="Regular user",
    )

    suffix = random.randint(1, 999999)

    user = User(
        username=f"perfuser_{suffix}",
        full_name=f"Performance User {suffix}",
        email=f"perfuser_{suffix}@example.com",
        hashed_password=await get_password_hash_fast_async("Password123"),
        is_active=True,
    )  # type: ignore[call-arg]

    user.role = role
    perf_uow.session.add(user)

    await perf_uow.session.commit()
    await perf_uow.session.refresh(user)

    yield user


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def perf_admin_user(perf_uow: UnitOfWork) -> User:
    """
    Creates admin user for performance tests.
    """
    existing_admin = await user_repo.get_user(
        session=perf_uow.session,
        username="perfadmin",
    )
    if existing_admin:
        return existing_admin

    admin_role = await perf_uow.roles.get_or_create(
        session=perf_uow.session,
        name=RoleEnum.ADMIN,
    )

    hashed_password = await get_password_hash_fast_async("AdminPassword123")

    admin_user = User(
        username="perfadmin",
        email="perfadmin@example.com",
        hashed_password=hashed_password,
        full_name="Performance Admin",
        is_active=True,
    )  # type: ignore[call-arg]

    admin_user.role = admin_role

    perf_uow.session.add(admin_user)
    await perf_uow.session.commit()
    await perf_uow.session.refresh(admin_user)

    return admin_user


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def perf_admin_headers(
    perf_client: AsyncClient,
    perf_admin_user: User,
) -> dict[str, str]:
    """
    Provides authorization headers for admin user in performance tests.
    """
    login_response = await perf_client.post(
        "/api/v1/auth/login",
        json={
            "username": perf_admin_user.username,
            "password": "AdminPassword123",
            "fingerprint": "perf_admin_test",
        },
    )

    tokens = login_response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="session")
def benchmark_config() -> dict[str, Any]:
    """
    Provides configuration for benchmark tests.
    """
    return {
        "min_rounds": 3,
        "warmup_iterations": 1,
    }


@pytest.fixture(scope="session")
def benchmark_api_config() -> dict[str, Any]:
    """
    Provides configuration for API benchmark tests.
    """
    return {
        "min_rounds": 3,
        "warmup_iterations": 1,
    }


@pytest.fixture(scope="session")
def benchmark_database_config() -> dict[str, Any]:
    """
    Provides configuration for database benchmark tests.
    """
    return {
        "min_rounds": 5,
        "warmup_iterations": 2,
    }
