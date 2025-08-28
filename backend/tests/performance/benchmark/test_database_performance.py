"""
Database operation performance tests.
"""

import asyncio
import random
from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio

from app.models.domain.role import RoleEnum
from app.models.domain.user import User
from app.models.schemas.user import UserCreate, UserUpdate
from app.repositories.unit_of_work import UnitOfWork
from app.utils.password import get_password_hash_fast_async


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def cleanup_database_users(
    perf_uow: UnitOfWork, perf_test_user: User
) -> AsyncGenerator[None, None]:
    """
    Cleanup fixture that runs after all database tests to delete created users.
    """
    yield

    users_for_delete = TestDatabasePerformance.created_usernames + [
        perf_test_user.username,
    ]

    for username in users_for_delete:
        user = await perf_uow.users.get_user(
            session=perf_uow.session, username=username
        )
        if user:
            sessions = await perf_uow.sessions.get_by_user_id(perf_uow.session, user.id)
            for session_obj in sessions:
                await perf_uow.sessions.delete(
                    session=perf_uow.session, obj=session_obj
                )

            await perf_uow.users.delete(session=perf_uow.session, obj=user)

    TestDatabasePerformance.created_usernames.clear()


class TestDatabasePerformance:
    """
    Database operation performance tests.
    """

    created_usernames: list[str] = []

    def test_user_creation_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        User creation performance test.
        """

        def _create_user() -> User:
            suffix = random.randint(1, 999999)
            username = f"benchuser_{suffix}"
            user_data = UserCreate(
                username=username,
                email=f"benchuser_{suffix}@example.com",
                password="Password123",
                full_name=f"Perf DB Signup User {suffix}",
                role=RoleEnum.USER,
            )

            self.__class__.created_usernames.append(username)

            async def _async_create() -> User:
                result = await perf_uow.users.create_user(
                    session=perf_uow.session,
                    obj_in=user_data,
                )
                await perf_uow.session.commit()
                return result

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_create())

        result = benchmark.pedantic(
            _create_user,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert result is not None
        assert result.username.startswith("benchuser_")

    def test_user_creation_performance_optimized(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        Optimized user creation performance test.
        """
        loop = asyncio.get_event_loop()
        role = loop.run_until_complete(
            perf_uow.roles.get_or_create(session=perf_uow.session, name=RoleEnum.USER),
        )

        def _create_user_optimized() -> User:
            suffix = random.randint(1, 999999)
            username = f"optuser_{suffix}"

            self.__class__.created_usernames.append(username)

            async def _async_create() -> User:
                hashed_password = await get_password_hash_fast_async("Password123")

                user = User(
                    username=username,
                    email=f"optuser_{suffix}@example.com",
                    hashed_password=hashed_password,
                    full_name=f"Perf DB Signup Opt User {suffix}",
                    is_active=True,
                )  # type: ignore[call-arg]
                user.role = role

                perf_uow.session.add(user)
                await perf_uow.session.flush()
                await perf_uow.session.refresh(user)
                await perf_uow.session.commit()
                return user

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_create())

        result = benchmark.pedantic(
            _create_user_optimized,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert result is not None
        assert result.username.startswith("optuser_")

    def test_user_creation_batch_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        Batch user creation performance test.
        """
        loop = asyncio.get_event_loop()
        role = loop.run_until_complete(
            perf_uow.roles.get_or_create(session=perf_uow.session, name=RoleEnum.USER),
        )

        def _create_users_batch() -> list[User]:
            async def _batch_create() -> list[User]:
                users = []
                for i in range(5):
                    suffix = f"{random.randint(1, 999999)}_{i}"
                    username = f"batchuser_{suffix}"

                    self.__class__.created_usernames.append(username)

                    user = User(
                        username=username,
                        email=f"batchuser_{suffix}@example.com",
                        hashed_password=await get_password_hash_fast_async(
                            "Password123"
                        ),
                        full_name=f"Perf DB Signup Batch User {suffix}",
                        is_active=True,
                    )  # type: ignore[call-arg]
                    user.role = role
                    users.append(user)

                perf_uow.session.add_all(users)
                await perf_uow.session.commit()
                return users

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_batch_create())

        result = benchmark.pedantic(
            _create_users_batch,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert len(result) == 5
        assert all(user.username.startswith("batchuser_") for user in result)

    def test_user_retrieval_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        perf_test_user: User,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        User retrieval by ID performance test.
        """

        def _get_user() -> Any:
            async def _async_get() -> Any:
                result = await perf_uow.users.get_by_user_id(
                    session=perf_uow.session,
                    user_id=perf_test_user.id,
                )
                await perf_uow.session.commit()
                return result

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_get())

        result = benchmark.pedantic(
            _get_user,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert result is not None
        assert result.id == perf_test_user.id

    def test_user_update_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        perf_test_user: User,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        User update performance test.
        """

        def _update_user() -> Any:
            update_data = UserUpdate(
                full_name=f"Updated Name {random.randint(1, 1000)}",
            )

            async def _async_update() -> Any:
                result = await perf_uow.users.update_user(
                    session=perf_uow.session,
                    current_user=perf_test_user,
                    obj_in=update_data,
                )
                await perf_uow.session.commit()
                return result

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_update())

        result = benchmark.pedantic(
            _update_user,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert result is not None
        assert "Updated Name" in result.full_name

    def test_users_list_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        perf_test_user: User,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        Users list retrieval performance test.
        """

        def _get_users() -> list[User]:
            async def _async_get() -> list[User]:
                result = await perf_uow.users.get_users(
                    session=perf_uow.session,
                    skip=0,
                    limit=50,
                )
                await perf_uow.session.commit()
                return result

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_get())

        result = benchmark.pedantic(
            _get_users,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert isinstance(result, list)
        assert len(result) <= 50

    def test_user_search_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        perf_test_user: User,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        User search by username performance test.
        """

        def _search_user() -> Any:
            async def _async_search() -> Any:
                result = await perf_uow.users.get_user(
                    session=perf_uow.session,
                    username=perf_test_user.username,
                )
                await perf_uow.session.commit()
                return result

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_search())

        result = benchmark.pedantic(
            _search_user,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert result is not None
        assert result.username == perf_test_user.username

    def test_role_operations_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        Role operations performance test.
        """

        def _get_role() -> Any:
            async def _async_get() -> Any:
                result = await perf_uow.roles.get_or_create(
                    session=perf_uow.session,
                    name=RoleEnum.USER,
                )
                await perf_uow.session.commit()
                return result

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_get())

        result = benchmark.pedantic(
            _get_role,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert result is not None
        assert result.name == RoleEnum.USER

    def test_session_operations_performance(
        self,
        benchmark: Any,
        perf_uow: UnitOfWork,
        perf_test_user: User,
        benchmark_database_config: dict[str, Any],
    ) -> None:
        """
        Session operations performance test.
        """

        def _create_session() -> Any:
            async def _async_create() -> Any:
                result = await perf_uow.sessions.create_or_update_session(
                    session=perf_uow.session,
                    user_id=perf_test_user.id,
                    refresh_token=f"token_{random.randint(1, 999999)}",
                    fingerprint=f"fp_{random.randint(1, 999999)}",
                )
                await perf_uow.session.commit()
                return result

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_async_create())

        result = benchmark.pedantic(
            _create_session,
            rounds=benchmark_database_config["min_rounds"],
            warmup_rounds=benchmark_database_config["warmup_iterations"],
        )

        assert result is not None
        assert result.user_id == perf_test_user.id
