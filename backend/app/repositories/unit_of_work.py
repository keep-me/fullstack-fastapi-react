"""
Unit of Work pattern implementation for managing database transactions.
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.repositories.permission import PermissionRepository
from app.repositories.role import RoleRepository
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository

T = TypeVar("T")
logger = logging.getLogger("app.repositories.unit_of_work")


class UnitOfWork:
    """
    Unit of Work pattern implementation for managing database transactions.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the unit of work with a database session.
        """
        self._session = session
        self.users = UserRepository()
        self.sessions = SessionRepository()
        self.roles = RoleRepository()
        self.permissions = PermissionRepository()
        logger.debug("Unit of Work initialized")

    async def __aenter__(self) -> "UnitOfWork":
        """
        Enter the async context manager.
        """
        logger.debug("Entering Unit of Work context")
        return self

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> None:
        """
        Exit the async context manager.
        """
        if exc_type is not None:
            logger.warning(f"Exception in Unit of Work: {exc_val}")
            await self.rollback()

    async def commit(self) -> None:
        """
        Commit the current transaction.
        """
        logger.debug("Committing transaction")
        await self._session.commit()

    async def rollback(self) -> None:
        """
        Rollback the current transaction.
        """
        logger.warning("Rolling back transaction")
        await self._session.rollback()

    @property
    def session(self) -> AsyncSession:
        """
        Get the current database session.
        """
        return self._session


async def get_uow(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[UnitOfWork]:
    """
    Dependency for getting a Unit of Work instance.
    """
    uow = UnitOfWork(session)
    try:
        logger.debug("Providing Unit of Work instance")
        yield uow
        await uow.commit()
    except Exception as e:
        logger.error(f"Error in Unit of Work: {e!s}")
        await uow.rollback()
        raise
