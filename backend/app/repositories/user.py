"""
User repository for the application.
"""

import logging
from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions.types.database import DatabaseError
from app.models.domain.user import User
from app.models.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository
from app.repositories.role import role_repo
from app.repositories.session import session_repo
from app.utils.cache import cached, invalidate_cache
from app.utils.password import get_password_hash_async

logger = logging.getLogger("app.repositories.user")


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    User repository for database operations related to users.
    """

    def __init__(self) -> None:
        """
        Initialize the user repository.
        """
        super().__init__(User)

    @cached(ex=settings.CACHE_EXPIRE_SECONDS)
    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> User | None:
        """
        Get user by user_id with caching and roles loaded.
        """
        logger.debug(f"Getting user by ID: {user_id}")
        query = (
            select(self.model)
            .options(selectinload(self.model.role))
            .where(self.model.id == user_id)
        )
        result = await session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_user(
        self,
        session: AsyncSession,
        username: str | None = None,
        email: str | None = None,
    ) -> User | None:
        """
        Get user by username or email.
        """
        logger.debug(f"Getting user by username: {username} or email: {email}")
        conditions = []

        if username is not None:
            conditions.append(User.username == username.lower())
        if email is not None:
            conditions.append(User.email == email.lower())

        if not conditions:
            return None

        result = await session.execute(
            select(User).options(selectinload(User.role)).where(or_(*conditions)),
        )
        return result.unique().scalar_one_or_none()

    async def get_users(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Get list of users with pagination.
        """
        logger.debug(f"Getting users with skip={skip}, limit={limit}")

        return await self.get_multi(
            session=session,
            skip=skip,
            limit=limit,
            options=[selectinload(User.role)],
        )

    async def create_user(self, session: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create new user with async password hashing.
        """
        logger.info(f"Creating new user: {obj_in.username}")
        try:
            role = await role_repo.get_or_create(session, obj_in.role)
            user_data = obj_in.model_dump(exclude={"password", "role"})
            user_data["hashed_password"] = await get_password_hash_async(
                obj_in.password,
            )
            db_obj = self.model(**user_data)
            db_obj.role = role
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await session.rollback()
            if (
                hasattr(e, "orig")
                and e.orig is not None
                and hasattr(e.orig, "args")
                and e.orig.args
            ):
                if "username" in e.orig.args[0]:
                    error_message = "integrity_error_username"
                elif "email" in e.orig.args[0]:
                    error_message = "integrity_error_email"
                else:
                    error_message = "integrity_error"
            raise DatabaseError(error_message)

    @invalidate_cache()
    async def update_user(
        self,
        session: AsyncSession,
        *,
        current_user: User,
        obj_in: UserUpdate,
    ) -> User:
        """
        Update existing user.
        """
        logger.debug(f"Updating user: {current_user.id}")

        update_data = obj_in.model_dump(
            exclude_unset=True,
            exclude={"role", "password"},
        )

        for field, value in update_data.items():
            setattr(current_user, field, value)

        if obj_in.role:
            role = await role_repo.get_or_create(session, obj_in.role)
            current_user.role = role

        if obj_in.password:
            current_user.hashed_password = await get_password_hash_async(
                obj_in.password,
            )

        session.add(current_user)
        await session.flush()
        await session.refresh(current_user)

        return current_user

    @invalidate_cache()
    async def update_password(
        self,
        session: AsyncSession,
        *,
        user: User,
        new_password: str,
    ) -> User:
        """
        Update user password with async hashing.
        """
        logger.debug(f"Updating password for user: {user.id}")
        hashed_password = await get_password_hash_async(new_password)

        stmt = (
            update(User)
            .where(User.id == user.id)
            .values(hashed_password=hashed_password)
        )
        await session.execute(stmt)
        await session.flush()

        user.hashed_password = hashed_password

        return user

    @invalidate_cache()
    async def delete_user(self, session: AsyncSession, *, user: User) -> User:
        """
        Delete user by setting is_active to False.
        """
        logger.info(f"Deactivating user: {user.id}")

        sessions = await session_repo.get_by_user_id(session, user.id)
        for session_obj in sessions:
            await session_repo.delete(session=session, obj=session_obj)

        stmt = update(User).where(User.id == user.id).values(is_active=False)
        await session.execute(stmt)
        await session.flush()

        user.is_active = False
        return user


user_repo = UserRepository()
