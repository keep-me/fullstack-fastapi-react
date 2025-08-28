"""
API endpoint performance tests.
"""

import asyncio
import random
from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response

from app.models.domain.role import RoleEnum
from app.models.domain.user import User
from app.repositories.unit_of_work import UnitOfWork


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def cleanup_created_users(
    perf_uow: UnitOfWork, perf_test_user: User, perf_admin_user: User
) -> AsyncGenerator[None, None]:
    """
    Cleanup fixture that runs after all tests to delete created users.
    """
    yield

    users_for_delete = TestAPIPerformance.created_usernames + [
        perf_test_user.username,
        perf_admin_user.username,
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

    TestAPIPerformance.created_usernames.clear()


class TestAPIPerformance:
    """
    API endpoint performance tests.
    """

    created_usernames: list[str] = []

    def test_health_check_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        Health check endpoint performance test.
        """

        def _health_check() -> Response:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(perf_client.get("/health"))

        result = benchmark.pedantic(
            _health_check,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["data"]["status"] == "healthy"

    def test_user_registration_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        benchmark_api_config: dict[str, Any],
        mock_send_email: Any,
        perf_uow: UnitOfWork,
    ) -> None:
        """
        User registration performance test.
        """

        def _register_user() -> Response:
            suffix = random.randint(1, 999999)
            username = f"apiuser_{suffix}"
            user_data = {
                "username": username,
                "email": f"apiuser_{suffix}@example.com",
                "password": "Password123",
                "full_name": f"Perf API Signup User {suffix}",
            }

            self.__class__.created_usernames.append(username)

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                perf_client.post("/api/v1/auth/signup", json=user_data),
            )

        result = benchmark.pedantic(
            _register_user,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_201_CREATED
        assert "username" in result.json()

    def test_user_login_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_test_user: User,
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        User login performance test.
        """

        def _login_user() -> Response:
            login_data = {
                "username": perf_test_user.username,
                "password": "Password123",
                "fingerprint": f"fp_{random.randint(1, 999999)}",
            }
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                perf_client.post("/api/v1/auth/login", json=login_data),
            )

        result = benchmark.pedantic(
            _login_user,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_200_OK
        assert "access_token" in result.json()
        assert "refresh_token" in result.json()

    def test_get_users_list_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_admin_headers: dict[str, Any],
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        Get users list performance test.
        """

        def _get_users() -> Response:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                perf_client.get("/api/v1/users/", headers=perf_admin_headers),
            )

        result = benchmark.pedantic(
            _get_users,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_200_OK
        assert isinstance(result.json(), list)

    def test_get_current_user_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_test_user: User,
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        Get current user performance test.
        """

        def _get_current_user() -> Response:
            loop = asyncio.get_event_loop()
            login_response = loop.run_until_complete(
                perf_client.post(
                    "/api/v1/auth/login",
                    json={
                        "username": perf_test_user.username,
                        "password": "Password123",
                        "fingerprint": "perf_test",
                    },
                ),
            )
            tokens = login_response.json()
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}

            response = loop.run_until_complete(
                perf_client.get("/api/v1/users/me", headers=headers),
            )
            return response

        result = benchmark.pedantic(
            _get_current_user,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_200_OK
        assert result.json()["username"] == perf_test_user.username

    def test_update_user_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_test_user: User,
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        Update user profile performance test.
        """

        def _update_user() -> Response:
            loop = asyncio.get_event_loop()
            login_response = loop.run_until_complete(
                perf_client.post(
                    "/api/v1/auth/login",
                    json={
                        "username": perf_test_user.username,
                        "password": "Password123",
                        "fingerprint": "perf_test",
                    },
                ),
            )
            tokens = login_response.json()
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}

            update_data = {"full_name": f"Updated Name {random.randint(1, 1000)}"}
            response = loop.run_until_complete(
                perf_client.patch(
                    "/api/v1/users/me", headers=headers, json=update_data
                ),
            )
            return response

        result = benchmark.pedantic(
            _update_user,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_200_OK
        assert "Updated Name" in result.json()["full_name"]

    def test_create_user_by_admin_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_admin_headers: dict[str, Any],
        benchmark_api_config: dict[str, Any],
        mock_send_email: Any,
    ) -> None:
        """
        Admin user creation performance test.
        """

        def _create_user() -> Response:
            suffix = random.randint(1, 999999)
            username = f"adminuser_{suffix}"
            user_data = {
                "username": username,
                "email": f"adminuser_{suffix}@example.com",
                "password": "Password123",
                "full_name": f"Perf Admin Create User {suffix}",
                "role": RoleEnum.USER,
            }

            self.__class__.created_usernames.append(username)

            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                perf_client.post(
                    "/api/v1/users/",
                    headers=perf_admin_headers,
                    json=user_data,
                ),
            )

        result = benchmark.pedantic(
            _create_user,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_201_CREATED
        assert "username" in result.json()

    def test_logout_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_test_user: User,
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        Logout performance test.
        """

        def _logout() -> Response:
            loop = asyncio.get_event_loop()
            login_response = loop.run_until_complete(  # noqa: F841
                perf_client.post(
                    "/api/v1/auth/login",
                    json={
                        "username": perf_test_user.username,
                        "password": "Password123",
                        "fingerprint": "perf_test",
                    },
                ),
            )

            response = loop.run_until_complete(perf_client.get("/api/v1/auth/logout"))
            return response

        result = benchmark.pedantic(
            _logout,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_200_OK

    def test_token_refresh_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_test_user: User,
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        Token refresh performance test.
        """

        def _refresh_token() -> Response:
            loop = asyncio.get_event_loop()
            login_response = loop.run_until_complete(
                perf_client.post(
                    "/api/v1/auth/login",
                    json={
                        "username": perf_test_user.username,
                        "password": "Password123",
                        "fingerprint": "perf_test",
                    },
                ),
            )

            login_data = login_response.json()
            access_token = login_data["access_token"]
            cookies = login_response.cookies

            response = loop.run_until_complete(
                perf_client.post(
                    "/api/v1/auth/refresh",
                    json={"fingerprint": "perf_test"},
                    headers={"Authorization": f"Bearer {access_token}"},
                    cookies=cookies,
                ),
            )
            return response

        result = benchmark.pedantic(
            _refresh_token,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert result.status_code == status.HTTP_200_OK
        assert "access_token" in result.json()

    def test_concurrent_requests_performance(
        self,
        benchmark: Any,
        perf_client: AsyncClient,
        perf_admin_headers: dict[str, Any],
        benchmark_api_config: dict[str, Any],
    ) -> None:
        """
        Concurrent requests performance test.
        """

        def _concurrent_requests() -> list[Response]:
            loop = asyncio.get_event_loop()

            results = []
            for i in range(5):
                result = loop.run_until_complete(
                    perf_client.get("/api/v1/users/", headers=perf_admin_headers),
                )
                results.append(result)

            return results

        results = benchmark.pedantic(
            _concurrent_requests,
            rounds=benchmark_api_config["min_rounds"],
            warmup_rounds=benchmark_api_config["warmup_iterations"],
        )

        assert len(results) == 5
        for result in results:
            assert result.status_code == status.HTTP_200_OK
            assert isinstance(result.json(), list)
