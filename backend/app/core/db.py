"""
Database connection management.
"""

import logging
from collections.abc import AsyncGenerator
from threading import Lock
from typing import Optional, cast

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.exceptions import DatabaseError
from app.models.domain.role import RoleEnum
from app.models.domain.user import User
from app.models.schemas.user import UserCreate
from app.repositories.role import role_repo
from app.repositories.user import user_repo


class DatabaseManager:
    """
    Thread-safe Singleton for managing database connections.
    """

    _instance: Optional["DatabaseManager"] = None
    _lock: Lock = Lock()
    _engine: AsyncEngine | None = None
    _session_maker: async_sessionmaker[AsyncSession] | None = None

    def __new__(cls) -> "DatabaseManager":
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize database connection lazily
        """
        if not self._engine:
            with self._lock:
                if not self._engine:
                    logging.info("Initializing database engine...")
                    self._engine = create_async_engine(
                        str(settings.SQLALCHEMY_DATABASE_URI),
                        isolation_level=settings.DB_ISOLATION_LEVEL,
                        pool_size=settings.DB_POOL_SIZE,
                        max_overflow=settings.DB_MAX_OVERFLOW,
                        pool_timeout=settings.DB_POOL_TIMEOUT,
                        pool_recycle=settings.DB_POOL_RECYCLE,
                        echo=settings.DB_ECHO,
                    )
                    self._session_maker = async_sessionmaker[AsyncSession](
                        self._engine,
                        expire_on_commit=False,
                        autoflush=False,
                    )
                    logging.info("Database engine initialized.")

    @property
    def engine(self) -> AsyncEngine:
        """
        Get the engine instance.
        """
        if not self._engine:
            self.session_maker
        return cast("AsyncEngine", self._engine)

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        """
        Get the session maker instance.
        """
        if not self._session_maker:
            if not self._engine:
                with self._lock:
                    if not self._engine:
                        logging.info("Initializing database engine...")
                        self._engine = create_async_engine(
                            str(settings.SQLALCHEMY_DATABASE_URI),
                            isolation_level=settings.DB_ISOLATION_LEVEL,
                            pool_size=settings.DB_POOL_SIZE,
                            max_overflow=settings.DB_MAX_OVERFLOW,
                            pool_timeout=settings.DB_POOL_TIMEOUT,
                            pool_recycle=settings.DB_POOL_RECYCLE,
                            echo=settings.DB_ECHO,
                        )
                        self._session_maker = async_sessionmaker[AsyncSession](
                            self._engine,
                            expire_on_commit=False,
                            autoflush=False,
                        )
                        logging.info("Database engine initialized.")

        return cast("async_sessionmaker[AsyncSession]", self._session_maker)

    async def cleanup(self) -> None:
        """
        Cleanup database connections.
        """
        if self._engine:
            logging.info("Cleaning up database connections...")
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None
            logging.info("Database connections cleaned up.")


db_manager = DatabaseManager()


async def get_session() -> AsyncGenerator[AsyncSession]:
    """
    Database Session Generator with enhanced error handling.
    """
    async with db_manager.session_maker() as session:
        yield session


async def init_db(session: AsyncSession) -> User | None:
    """
    Initialize Database with first superuser.
    """

    try:
        logging.info("Initializing roles...")
        await role_repo.initialize_roles(session)
        logging.info("Roles initialized successfully.")

        user = await user_repo.get_user(
            session=session,
            username=settings.FIRST_SUPERUSER_USERNAME,
        )

        if not user:
            logging.info("Creating initial superuser.")
            user_in = UserCreate(
                username=settings.FIRST_SUPERUSER_USERNAME,
                full_name=settings.FIRST_SUPERUSER_NAME,
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                role=RoleEnum.ADMIN,
            )
            user = await user_repo.create_user(
                session=session,
                obj_in=user_in,
            )
            logging.info("Initial superuser created.")
        return user
    except SQLAlchemyError as e:
        logging.exception(f"Database error during initialization: {e}")
        raise DatabaseError("query_failed", str(e))
    except Exception as e:
        logging.exception(f"Error initializing database: {e}")
        raise DatabaseError("connection_failed", str(e))
