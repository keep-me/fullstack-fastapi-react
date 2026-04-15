"""
Role repository for the application.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.domain.permission import Permission
from app.models.domain.role import Role, RoleEnum
from app.models.domain.user import User
from app.models.schemas.role import RoleCreate, RoleUpdate
from app.repositories.base import BaseRepository
from app.repositories.permission import permission_repo

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
        Get role by name with permissions loaded.
        """
        logger.debug(f"Getting role by name: {name}")
        query = (
            select(self.model)
            .options(selectinload(self.model.permissions))
            .where(self.model.name == name)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_by_id_with_permissions(
        self,
        session: AsyncSession,
        role_id: int,
    ) -> Role | None:
        """
        Get role by ID with permissions loaded.
        """
        logger.debug(f"Getting role by ID with permissions: {role_id}")
        query = (
            select(self.model)
            .options(selectinload(self.model.permissions))
            .where(self.model.id == role_id)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_all_with_permissions(
        self,
        session: AsyncSession,
    ) -> list[Role]:
        """
        Get all roles with permissions loaded.
        """
        logger.debug("Getting all roles with permissions")
        query = (
            select(self.model)
            .options(selectinload(self.model.permissions))
            .order_by(self.model.id)
        )
        result = await session.execute(query)
        return list(result.scalars().unique().all())

    async def get_role_user_count(
        self,
        session: AsyncSession,
        role_id: int,
    ) -> int:
        """
        Get the number of users assigned to a role.
        """
        logger.debug(f"Getting user count for role: {role_id}")
        query = select(func.count(User.id)).where(User.role_id == role_id)
        result = await session.execute(query)
        count = result.scalar()
        return count if count is not None else 0

    async def _create_new_role(
        self,
        session: AsyncSession,
        name: RoleEnum,
        description: str | None,
        role_id: int | None = None,
        permissions: list[Permission] | None = None,
    ) -> Role:
        """
        Create new role with optional specific ID and permissions.
        """
        logger.info(f"Creating new role: {name}")

        if role_id:
            role = Role(id=role_id, name=name)  # type: ignore[call-arg]
            if description is not None:
                role.description = description
            if permissions:
                role.permissions = permissions
            session.add(role)
            await session.flush()
            await session.refresh(role)
            logger.info(f"Created role {name} with ID {role_id}")
        else:
            role_data = RoleCreate(name=name, description=description)
            role = await self.create(session=session, obj_in=role_data)
            if permissions:
                role.permissions = permissions
                await session.flush()
                await session.refresh(role)

        return role

    async def create_role_with_permissions(
        self,
        session: AsyncSession,
        obj_in: RoleCreate,
    ) -> Role:
        """
        Create a new role with permissions.
        """
        logger.info(f"Creating role with permissions: {obj_in.name}")

        permissions = []
        if obj_in.permissions:
            permissions = await permission_repo.get_by_names(session, obj_in.permissions)

        role = Role(
            name=obj_in.name,
            description=obj_in.description,
        )
        if permissions:
            role.permissions = permissions

        session.add(role)
        await session.flush()
        await session.refresh(role)

        return role

    async def update_role_with_permissions(
        self,
        session: AsyncSession,
        db_obj: Role,
        obj_in: RoleUpdate,
    ) -> Role:
        """
        Update role with permissions.
        """
        logger.debug(f"Updating role: {db_obj.id}")

        update_data = obj_in.model_dump(exclude_unset=True, exclude={"permissions"})

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        if obj_in.permissions is not None:
            permissions = await permission_repo.get_by_names(session, obj_in.permissions)
            db_obj.permissions = permissions

        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)

        return db_obj

    async def get_or_create(
        self,
        session: AsyncSession,
        name: RoleEnum,
        description: str | None = None,
        role_id: int | None = None,
        permissions: list[Permission] | None = None,
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

        return await self._create_new_role(session, name, description, role_id, permissions)

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

    async def assign_permissions_to_role(
        self,
        session: AsyncSession,
        role_id: int,
        permission_ids: list[int],
    ) -> Role | None:
        """
        Assign permissions to a role.
        """
        logger.info(f"Assigning permissions {permission_ids} to role {role_id}")

        role = await self.get_by_id_with_permissions(session, role_id)
        if not role:
            return None

        permissions = await permission_repo.get_by_ids(session, permission_ids)
        role.permissions = permissions

        session.add(role)
        await session.flush()
        await session.refresh(role)

        return role

    async def add_permission_to_role(
        self,
        session: AsyncSession,
        role_id: int,
        permission_id: int,
    ) -> Role | None:
        """
        Add a single permission to a role.
        """
        logger.info(f"Adding permission {permission_id} to role {role_id}")

        role = await self.get_by_id_with_permissions(session, role_id)
        if not role:
            return None

        permission = await permission_repo.get(session, permission_id)
        if not permission:
            return None

        if permission not in role.permissions:
            role.permissions.append(permission)
            session.add(role)
            await session.flush()
            await session.refresh(role)

        return role

    async def remove_permission_from_role(
        self,
        session: AsyncSession,
        role_id: int,
        permission_id: int,
    ) -> Role | None:
        """
        Remove a permission from a role.
        """
        logger.info(f"Removing permission {permission_id} from role {role_id}")

        role = await self.get_by_id_with_permissions(session, role_id)
        if not role:
            return None

        permission = await permission_repo.get(session, permission_id)
        if not permission:
            return None

        if permission in role.permissions:
            role.permissions.remove(permission)
            session.add(role)
            await session.flush()
            await session.refresh(role)

        return role

    async def initialize_roles(self, session: AsyncSession) -> None:
        """
        Initialize all roles with descriptions, specific IDs, and default permissions.
        """
        logger.info("Initializing roles with specific IDs and permissions")

        all_permissions = await permission_repo.get_all(session)
        permission_map = {p.name: p for p in all_permissions}

        admin_permissions = list(all_permissions)

        manager_permission_names = [
            "user:read",
            "user:create",
            "user:update",
            "role:read",
            "endpoint:execute",
        ]
        manager_permissions = [
            permission_map[name] for name in manager_permission_names if name in permission_map
        ]

        user_permission_names = [
            "user:read",
            "endpoint:execute",
        ]
        user_permissions = [
            permission_map[name] for name in user_permission_names if name in permission_map
        ]

        guest_permission_names = [
            "endpoint:execute",
        ]
        guest_permissions = [
            permission_map[name] for name in guest_permission_names if name in permission_map
        ]

        roles_config = [
            (1, RoleEnum.ADMIN, "Administrator with full access", admin_permissions),
            (2, RoleEnum.MANAGER, "Manager with limited administrative access", manager_permissions),
            (3, RoleEnum.USER, "Regular user", user_permissions),
            (4, RoleEnum.GUEST, "Guest user with restricted access", guest_permissions),
        ]

        for role_id, role_name, description, permissions in roles_config:
            await self.get_or_create(
                session=session,
                name=role_name,
                description=description,
                role_id=role_id,
                permissions=permissions,
            )

        logger.info("Roles initialized successfully")


role_repo = RoleRepository()
