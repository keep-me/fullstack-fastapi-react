"""
Load testing configuration for different user types.
"""

import random
from collections.abc import Callable
from typing import Any

from fastapi import status
from locust import HttpUser, between, task


class SimpleUser(HttpUser):
    """
    Simple user for basic load testing.
    """

    wait_time: Callable[[], float] = between(1, 3)  # type: ignore[no-untyped-call]
    user_credentials: list[dict[str, Any]] = []

    def on_start(self) -> None:
        """
        Called when a user starts running.
        """
        self.register_and_login()

    def register_and_login(self) -> None:
        """
        Register a new user and then log in.
        """
        suffix = f"{random.randint(1, 9999999)}"
        self.username = f"loaduser_{suffix}"
        self.password = "Password123"
        self.fingerprint = f"load_fingerprint_{suffix}"

        register_data = {
            "username": self.username,
            "email": f"{self.username}@example.com",
            "password": self.password,
            "full_name": "Perf Load User",
        }
        with self.client.post(
            "/api/v1/auth/signup",
            json=register_data,
            name="/api/v1/auth/signup",
            catch_response=True,
        ) as response:
            if response.status_code != status.HTTP_201_CREATED:
                response.failure(
                    f"Registration failed with status {response.status_code}",
                )
                return

        self.login()

    def login(self) -> None:
        """
        Authenticate the user.
        """
        if (
            not hasattr(self, "username")
            or not hasattr(self, "password")
            or not hasattr(self, "fingerprint")
            or not self.username
            or not self.password
            or not self.fingerprint
        ):
            return

        login_data = {
            "username": self.username,
            "password": self.password,
            "fingerprint": self.fingerprint,
        }
        with self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            name="/api/v1/auth/login",
            catch_response=True,
        ) as response:
            if response.status_code == status.HTTP_200_OK:
                self.tokens = response.json()
                self.client.headers["Authorization"] = (
                    f"Bearer {self.tokens['access_token']}"
                )
            else:
                response.failure(f"Login failed with status {response.status_code}")

    @task(3)
    def view_health(self) -> None:
        """
        Check application health.
        """
        with self.client.get(
            "/health",
            name="/health",
            catch_response=True,
        ) as response:
            if response.status_code != status.HTTP_200_OK:
                response.failure(
                    f"Health check failed with status {response.status_code}",
                )

    @task(5)
    def view_profile(self) -> None:
        """
        View user profile.
        """
        if (
            not hasattr(self, "tokens")
            or not hasattr(self, "username")
            or not self.tokens
            or not self.username
        ):
            self.register_and_login()
            if not hasattr(self, "tokens") or not self.tokens:
                return

        with self.client.get(
            "/api/v1/users/me",
            name="/api/v1/users/me",
            catch_response=True,
        ) as response:
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                self.refresh_token()
            elif response.status_code != status.HTTP_200_OK:
                response.failure(
                    f"Profile view failed with status {response.status_code}",
                )

    @task(2)
    def update_profile(self) -> None:
        """
        Update user profile.
        """
        if (
            not hasattr(self, "tokens")
            or not hasattr(self, "username")
            or not self.tokens
            or not self.username
        ):
            self.register_and_login()
            if not hasattr(self, "tokens") or not self.tokens:
                return

        update_data = {"full_name": f"Updated User {random.randint(1, 1000)}"}

        with self.client.patch(
            "/api/v1/users/me",
            json=update_data,
            name="/api/v1/users/me",
            catch_response=True,
        ) as response:
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                self.refresh_token()
            elif response.status_code != status.HTTP_200_OK:
                response.failure(
                    f"Profile update failed with status {response.status_code}",
                )

    @task(1)
    def refresh_token(self) -> None:
        """
        Refresh authentication token.
        """
        if (
            not hasattr(self, "tokens")
            or not hasattr(self, "fingerprint")
            or not hasattr(self, "username")
            or not self.tokens
            or not self.fingerprint
            or not self.username
        ):
            self.register_and_login()
            if not hasattr(self, "tokens") or not self.tokens:
                return

        refresh_data = {"fingerprint": self.fingerprint}

        with self.client.post(
            "/api/v1/auth/refresh",
            json=refresh_data,
            name="/api/v1/auth/refresh",
            catch_response=True,
        ) as response:
            if response.status_code == status.HTTP_200_OK:
                self.tokens = response.json()
                self.client.headers["Authorization"] = (
                    f"Bearer {self.tokens['access_token']}"
                )
            else:
                response.failure(
                    f"Token refresh failed with status {response.status_code}",
                )

    @task(2)
    def delete_user(self) -> None:
        """
        Delete user.
        """
        if (
            not hasattr(self, "tokens")
            or not hasattr(self, "username")
            or not self.tokens
            or not self.username
        ):
            self.register_and_login()
            if not hasattr(self, "tokens") or not self.tokens:
                return

        with self.client.delete(
            "/api/v1/users/me",
            name="/api/v1/users/me",
            catch_response=True,
        ) as response:
            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                self.refresh_token()

                with self.client.delete(
                    "/api/v1/users/me",
                    name="/api/v1/users/me",
                    catch_response=True,
                ) as retry_response:
                    if retry_response.status_code == status.HTTP_200_OK:
                        retry_response.success()
                        self.username = ""
                        self.tokens = {}
                    else:
                        retry_response.failure(
                            f"Failed to delete user {self.username} on retry. Status: {retry_response.status_code}",
                        )
            elif response.status_code == status.HTTP_200_OK:
                response.success()
                self.username = ""
                self.tokens = {}
            else:
                response.failure(
                    f"Failed to delete user {self.username}. Status: {response.status_code}",
                )

    def on_stop(self) -> None:
        """
        Called when user stops running - cleanup.
        """
        if (
            hasattr(self, "tokens")
            and hasattr(self, "username")
            and self.tokens
            and self.username
        ):
            try:
                with self.client.delete(
                    "/api/v1/users/me",
                    name="/api/v1/users/me (cleanup)",
                    catch_response=True,
                ) as response:
                    if response.status_code == status.HTTP_200_OK:
                        response.success()
                    else:
                        response.failure(f"Failed to cleanup user {self.username}")
            except Exception:
                pass
