"""
Role repository for the application.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.role import Role, RoleEnum
from app.models.schemas.role import RoleCreate, RoleUpdate
from app.repositories.base import BaseRepository

logger = logging.getLogger("app.repositories.role")


class RoleRepository(BaseRepository[Role, RoleCreate, RoleUpdate]):
    """
    Repository for managing roles.
    """

    def __init__(self) -> None:
        """
        Initialize role repository.
        """
        super().__init__(Role)

    async def get_by_name(
        self,
        session: AsyncSession,
        name: RoleEnum,
    ) -> Role | None:
        """
        Get role by name.
        """
        logger.debug(f"Getting role by name: {name}")
        query = select(self.model).where(self.model.name == name)
        result = await session.execute(query)
        return result.scalars().first()

    async def _create_new_role(
        self,
        session: AsyncSession,
        name: RoleEnum,
        description: str | None,
        role_id: int | None = None,
    ) -> Role:
        """
        Create new role with optional specific ID.
        """
        logger.info(f"Creating new role: {name}")

        if role_id:
            role = Role(id=role_id, name=name)  # type: ignore[call-arg]
            if description is not None:
                role.description = description
            session.add(role)
            await session.flush()
            await session.refresh(role)
            logger.info(f"Created role {name} with ID {role_id}")
        else:
            role_data = RoleCreate(name=name, description=description)
            role = await self.create(session=session, obj_in=role_data)

        return role

    async def get_or_create(
        self,
        session: AsyncSession,
        name: RoleEnum,
        description: str | None = None,
        role_id: int | None = None,
    ) -> Role:
        """
        Get role by name or create if it doesn't exist.
        """
        existing_role = await self.get_by_name(session, name)

        if existing_role:
            return await self._update_role_description(
                session,
                existing_role,
                description,
            )

        return await self._create_new_role(session, name, description, role_id)

    async def _update_role_description(
        self,
        session: AsyncSession,
        role: Role,
        description: str | None,
    ) -> Role:
        """
        Update role description if it's not set and description is provided.
        """
        if description and not role.description:
            logger.info(f"Updating description for role: {role.name}")
            update_data = RoleUpdate(description=description)
            role = await self.update(session=session, db_obj=role, obj_in=update_data)
        return role

    async def initialize_roles(self, session: AsyncSession) -> None:
        """
        Initialize all roles with descriptions and specific IDs.
        """
        logger.info("Initializing roles with specific IDs")

        roles_config = [
            (1, RoleEnum.ADMIN, "Administrator with full access"),
            (2, RoleEnum.MANAGER, "Manager with limited administrative access"),
            (3, RoleEnum.USER, "Regular user"),
            (4, RoleEnum.GUEST, "Guest user with restricted access"),
        ]

        for role_id, role_name, description in roles_config:
            await self.get_or_create(
                session=session,
                name=role_name,
                description=description,
                role_id=role_id,
            )

        logger.info("Roles initialized successfully")


role_repo = RoleRepository()
