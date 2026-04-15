"""
Permission management endpoints.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.api.deps import (
    CurrentSuperUser,
    CurrentUser,
    PaginationDep,
    UnitOfWorkDep,
)
from app.core.exceptions import ValidationError
from app.models.schemas.role import (
    PermissionCreate,
    PermissionPublic,
    PermissionUpdate,
)
from app.utils.response import create_response

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/", response_model=list[PermissionPublic])
async def get_permissions(
    current_user: CurrentUser,
    uow: UnitOfWorkDep,
    pagination: PaginationDep,
) -> list[PermissionPublic]:
    """
    Get all permissions with pagination.
    Requires authentication.
    """
    permissions = await uow.permissions.get_all(session=uow.session)
    return [PermissionPublic.model_validate(perm) for perm in permissions]


@router.get("/by-resource/{resource}", response_model=list[PermissionPublic])
async def get_permissions_by_resource(
    current_user: CurrentUser,
    resource: str,
    uow: UnitOfWorkDep,
) -> list[PermissionPublic]:
    """
    Get permissions by resource.
    Requires authentication.
    """
    permissions = await uow.permissions.get_by_resource(session=uow.session, resource=resource)
    return [PermissionPublic.model_validate(perm) for perm in permissions]


@router.get("/{permission_id}", response_model=PermissionPublic)
async def get_permission_by_id(
    current_user: CurrentUser,
    permission_id: int,
    uow: UnitOfWorkDep,
) -> PermissionPublic:
    """
    Get permission by ID.
    Requires authentication.
    """
    permission = await uow.permissions.get(session=uow.session, id=permission_id)
    if not permission:
        raise ValidationError("permission_not_found")
    return PermissionPublic.model_validate(permission)


@router.post("/", response_model=PermissionPublic, status_code=status.HTTP_201_CREATED)
async def create_permission(
    current_superuser: CurrentSuperUser,
    permission_in: PermissionCreate,
    uow: UnitOfWorkDep,
) -> PermissionPublic:
    """
    Create a new permission.
    Requires admin privileges.
    """
    existing_permission = await uow.permissions.get_by_name(
        session=uow.session,
        name=permission_in.name,
    )
    if existing_permission:
        raise ValidationError("permission_exists")

    new_permission = await uow.permissions.create(
        session=uow.session,
        obj_in=permission_in,
    )
    return PermissionPublic.model_validate(new_permission)


@router.patch("/{permission_id}", response_model=PermissionPublic)
async def update_permission(
    current_superuser: CurrentSuperUser,
    permission_id: int,
    permission_in: PermissionUpdate,
    uow: UnitOfWorkDep,
) -> PermissionPublic:
    """
    Update a permission.
    Requires admin privileges.
    """
    permission = await uow.permissions.get(session=uow.session, id=permission_id)
    if not permission:
        raise ValidationError("permission_not_found")

    if permission_in.name and permission_in.name != permission.name:
        existing_permission = await uow.permissions.get_by_name(
            session=uow.session,
            name=permission_in.name,
        )
        if existing_permission:
            raise ValidationError("permission_exists")

    updated_permission = await uow.permissions.update(
        session=uow.session,
        db_obj=permission,
        obj_in=permission_in,
    )
    return PermissionPublic.model_validate(updated_permission)


@router.delete("/{permission_id}")
async def delete_permission(
    current_superuser: CurrentSuperUser,
    permission_id: int,
    uow: UnitOfWorkDep,
    request: Request,
) -> JSONResponse:
    """
    Delete a permission.
    Requires admin privileges.
    """
    permission = await uow.permissions.get(session=uow.session, id=permission_id)
    if not permission:
        raise ValidationError("permission_not_found")

    await uow.permissions.delete(session=uow.session, obj=permission)

    return create_response(
        status_code=status.HTTP_200_OK,
        message=f"Permission {permission.name} deleted successfully",
        request=request,
    )
