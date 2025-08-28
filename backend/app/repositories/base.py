"""
Base repository for the application.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseError
from app.utils.password import get_password_hash_async

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository implementing common CRUD operations.
    """

    def __init__(self, model: type[ModelType]):
        """
        Initialize repository with model class.
        """
        self.model = model

    async def get_by_id(self, session: AsyncSession, id: UUID) -> ModelType | None:
        """
        Get record by ID.
        """
        try:
            result = await session.execute(
                select(self.model).where(self.model.id == id),  # type: ignore[attr-defined]
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError("query_failed", str(e))

    async def get_multi(
        self,
        session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        options: list[Any] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelType]:
        """
        Get multiple records with pagination and optional filtering.
        """
        try:
            query = select(self.model)

            if hasattr(self.model, "is_active"):
                query = query.where(self.model.is_active.is_(True))  # type: ignore[attr-defined]

            if filters:
                for field_name, value in filters.items():
                    if hasattr(self.model, field_name):
                        query = query.where(getattr(self.model, field_name) == value)

            if options:
                for option in options:
                    query = query.options(option)

            arr_obj = await session.execute(query.offset(skip).limit(limit))

            if options:
                return list(arr_obj.unique().scalars().all())
            return list(arr_obj.scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseError("query_failed", str(e))

    async def create(
        self,
        session: AsyncSession,
        *,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        """
        Create new record with async password hashing.
        """
        try:
            obj_in_data = obj_in.model_dump(exclude={"password", "role"})

            if hasattr(obj_in, "password"):
                obj_in_data["hashed_password"] = await get_password_hash_async(
                    obj_in.password,
                )

            db_obj = self.model(**obj_in_data)
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            raise DatabaseError("integrity_error", str(e))
        except SQLAlchemyError as e:
            raise DatabaseError("query_failed", str(e))

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """
        Update existing record.
        """
        try:
            obj_data = jsonable_encoder(db_obj)
            update_data = obj_in.model_dump(exclude_unset=True)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])

            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            raise DatabaseError("integrity_error", str(e))
        except SQLAlchemyError as e:
            raise DatabaseError("query_failed", str(e))

    async def delete(self, session: AsyncSession, *, obj: ModelType) -> ModelType:
        """
        Delete record.
        """
        try:
            await session.delete(obj)
            await session.flush()
            return obj
        except SQLAlchemyError as e:
            raise DatabaseError("query_failed", str(e))
