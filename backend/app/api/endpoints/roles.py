"""
Role management endpoints.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.api.deps import (
    CurrentSuperUser,
    CurrentUser,
    PaginationDep,
    UnitOfWorkDep,
)
from app.core.exceptions import UserAccessError, ValidationError
from app.models.schemas.role import (
    AssignPermissionsRequest,
    RoleCreate,
    RolePublic,
    RoleUpdate,
    RoleWithUsers,
)
from app.utils.response import create_response

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=list[RolePublic])
async def get_roles(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    pagination: PaginationDep,
) -> list[RolePublic]:
    """
    Get all roles with pagination.
    Requires authentication.
    """
    roles = await uow.roles.get_all_with_permissions(session=uow.session)
    return [RolePublic.model_validate(role) for role in roles]


@router.get("/with-users", response_model=list[RoleWithUsers])
async def get_roles_with_user_count(
    current_superuser: CurrentSuperUser,
    uow: UnitOfWorkDep,
) -> list[RoleWithUsers]:
    """
    Get all roles with user count.
    Requires admin privileges.
    """
    roles = await uow.roles.get_all_with_permissions(session=uow.session)
    result = []
    for role in roles:
        user_count = await uow.roles.get_role_user_count(session=uow.session, role_id=role.id)
        role_public = RolePublic.model_validate(role)
        role_with_users = RoleWithUsers(
            id=role_public.id,
            name=role_public.name,
            description=role_public.description,
            permissions=role_public.permissions,
            user_count=user_count,
        )
        result.append(role_with_users)
    return result


@router.get("/{role_id}", response_model=RolePublic)
async def get_role_by_id(
    current_user: CurrentUser,
    role_id: int,
    uow: UnitOfWorkDep,
) -> RolePublic:
    """
    Get role by ID.
    Requires authentication.
    """
    role = await uow.roles.get_by_id_with_permissions(session=uow.session, role_id=role_id)
    if not role:
        raise ValidationError("role_not_found")
    return RolePublic.model_validate(role)


@router.post("/", response_model=RolePublic, status_code=status.HTTP_201_CREATED)
async def create_role(
    current_superuser: CurrentSuperUser,
    role_in: RoleCreate,
    uow: UnitOfWorkDep,
) -> RolePublic:
    """
    Create a new role.
    Requires admin privileges.
    """
    existing_role = await uow.roles.get_by_name(session=uow.session, name=role_in.name)
    if existing_role:
        raise ValidationError("role_exists")

    new_role = await uow.roles.create_role_with_permissions(
        session=uow.session,
        obj_in=role_in,
    )
    return RolePublic.model_validate(new_role)


@router.patch("/{role_id}", response_model=RolePublic)
async def update_role(
    current_superuser: CurrentSuperUser,
    role_id: int,
    role_in: RoleUpdate,
    uow: UnitOfWorkDep,
) -> RolePublic:
    """
    Update a role.
    Requires admin privileges.
    """
    role = await uow.roles.get_by_id_with_permissions(session=uow.session, role_id=role_id)
    if not role:
        raise ValidationError("role_not_found")

    if role_in.name and role_in.name != role.name:
        existing_role = await uow.roles.get_by_name(session=uow.session, name=role_in.name)
        if existing_role:
            raise ValidationError("role_exists")

    updated_role = await uow.roles.update_role_with_permissions(
        session=uow.session,
        db_obj=role,
        obj_in=role_in,
    )
    return RolePublic.model_validate(updated_role)


@router.delete("/{role_id}")
async def delete_role(
    current_superuser: CurrentSuperUser,
    role_id: int,
    uow: UnitOfWorkDep,
    request: Request,
) -> JSONResponse:
    """
    Delete a role.
    Requires admin privileges.
    Cannot delete roles that have users assigned.
    """
    role = await uow.roles.get(session=uow.session, id=role_id)
    if not role:
        raise ValidationError("role_not_found")

    user_count = await uow.roles.get_role_user_count(session=uow.session, role_id=role_id)
    if user_count > 0:
        raise UserAccessError("role_has_users")

    await uow.roles.delete(session=uow.session, obj=role)

    return create_response(
        status_code=status.HTTP_200_OK,
        message=f"Role {role.name} deleted successfully",
        request=request,
    )


@router.post("/{role_id}/permissions", response_model=RolePublic)
async def assign_permissions_to_role(
    current_superuser: CurrentSuperUser,
    role_id: int,
    permission_ids: list[int],
    uow: UnitOfWorkDep,
) -> RolePublic:
    """
    Assign permissions to a role.
    Requires admin privileges.
    """
    role = await uow.roles.assign_permissions_to_role(
        session=uow.session,
        role_id=role_id,
        permission_ids=permission_ids,
    )
    if not role:
        raise ValidationError("role_not_found")
    return RolePublic.model_validate(role)


@router.post("/{role_id}/permissions/{permission_id}", response_model=RolePublic)
async def add_permission_to_role(
    current_superuser: CurrentSuperUser,
    role_id: int,
    permission_id: int,
    uow: UnitOfWorkDep,
) -> RolePublic:
    """
    Add a single permission to a role.
    Requires admin privileges.
    """
    role = await uow.roles.add_permission_to_role(
        session=uow.session,
        role_id=role_id,
        permission_id=permission_id,
    )
    if not role:
        raise ValidationError("role_or_permission_not_found")
    return RolePublic.model_validate(role)


@router.delete("/{role_id}/permissions/{permission_id}", response_model=RolePublic)
async def remove_permission_from_role(
    current_superuser: CurrentSuperUser,
    role_id: int,
    permission_id: int,
    uow: UnitOfWorkDep,
) -> RolePublic:
    """
    Remove a permission from a role.
    Requires admin privileges.
    """
    role = await uow.roles.remove_permission_from_role(
        session=uow.session,
        role_id=role_id,
        permission_id=permission_id,
    )
    if not role:
        raise ValidationError("role_or_permission_not_found")
    return RolePublic.model_validate(role)
