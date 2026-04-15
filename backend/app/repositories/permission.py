"""
Permission repository for the application.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.domain.permission import Permission, PermissionEnum
from app.models.schemas.role import PermissionCreate, PermissionUpdate
from app.repositories.base import BaseRepository

logger = logging.getLogger("app.repositories.permission")


class PermissionRepository(BaseRepository[Permission, PermissionCreate, PermissionUpdate]):
    """
    Repository for managing permissions.
    """

    def __init__(self) -> None:
        """
        Initialize permission repository.
        """
        super().__init__(Permission)

    async def get_by_name(
        self,
        session: AsyncSession,
        name: str,
    ) -> Permission | None:
        """
        Get permission by name.
        """
        logger.debug(f"Getting permission by name: {name}")
        query = select(self.model).where(self.model.name == name)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_ids(
        self,
        session: AsyncSession,
        permission_ids: list[int],
    ) -> list[Permission]:
        """
        Get permissions by list of IDs.
        """
        logger.debug(f"Getting permissions by IDs: {permission_ids}")
        if not permission_ids:
            return []
        query = select(self.model).where(self.model.id.in_(permission_ids))
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_by_names(
        self,
        session: AsyncSession,
        permission_names: list[str],
    ) -> list[Permission]:
        """
        Get permissions by list of names.
        """
        logger.debug(f"Getting permissions by names: {permission_names}")
        if not permission_names:
            return []
        query = select(self.model).where(self.model.name.in_(permission_names))
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self,
        session: AsyncSession,
    ) -> list[Permission]:
        """
        Get all permissions.
        """
        logger.debug("Getting all permissions")
        query = select(self.model).order_by(self.model.id)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_by_resource(
        self,
        session: AsyncSession,
        resource: str,
    ) -> list[Permission]:
        """
        Get permissions by resource.
        """
        logger.debug(f"Getting permissions by resource: {resource}")
        query = select(self.model).where(self.model.resource == resource).order_by(self.model.id)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def initialize_permissions(self, session: AsyncSession) -> None:
        """
        Initialize all default permissions.
        """
        logger.info("Initializing default permissions")

        permissions_config = [
            (1, PermissionEnum.USER_READ, "Read user information", "user", "read"),
            (2, PermissionEnum.USER_CREATE, "Create new users", "user", "create"),
            (3, PermissionEnum.USER_UPDATE, "Update user information", "user", "update"),
            (4, PermissionEnum.USER_DELETE, "Delete users", "user", "delete"),
            (5, PermissionEnum.ROLE_READ, "Read role information", "role", "read"),
            (6, PermissionEnum.ROLE_CREATE, "Create new roles", "role", "create"),
            (7, PermissionEnum.ROLE_UPDATE, "Update role information", "role", "update"),
            (8, PermissionEnum.ROLE_DELETE, "Delete roles", "role", "delete"),
            (9, PermissionEnum.PERMISSION_READ, "Read permission information", "permission", "read"),
            (10, PermissionEnum.PERMISSION_CREATE, "Create new permissions", "permission", "create"),
            (11, PermissionEnum.PERMISSION_UPDATE, "Update permission information", "permission", "update"),
            (12, PermissionEnum.PERMISSION_DELETE, "Delete permissions", "permission", "delete"),
            (13, PermissionEnum.ENDPOINT_EXECUTE, "Execute API endpoints", "endpoint", "execute"),
            (14, PermissionEnum.ENDPOINT_MANAGE, "Manage API endpoints", "endpoint", "manage"),
        ]

        for perm_id, perm_name, description, resource, action in permissions_config:
            existing = await self.get_by_name(session, perm_name)
            if not existing:
                permission = Permission(
                    id=perm_id,
                    name=perm_name,
                    description=description,
                    resource=resource,
                    action=action,
                )
                session.add(permission)
                logger.info(f"Created permission: {perm_name}")

        await session.flush()
        logger.info("Permissions initialized successfully")


permission_repo = PermissionRepository()
