from typing import Any

from pydantic import BaseModel, field_validator

from app.core.exceptions import ValidationError
from app.models.domain.permission import Permission, PermissionEnum
from app.models.domain.role import Role, RoleEnum


class PermissionBase(BaseModel):
    name: str
    description: str | None = None
    resource: str
    action: str

    @field_validator("name")
    @classmethod
    def name_validator(cls, v: str) -> str:
        if not v or len(v) > 50:
            raise ValidationError("invalid_permission_name")
        return v.strip()

    @field_validator("resource")
    @classmethod
    def resource_validator(cls, v: str) -> str:
        if not v or len(v) > 30:
            raise ValidationError("invalid_resource")
        return v.strip()

    @field_validator("action")
    @classmethod
    def action_validator(cls, v: str) -> str:
        if not v or len(v) > 20:
            raise ValidationError("invalid_action")
        return v.strip()


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    resource: str | None = None
    action: str | None = None

    @field_validator("name")
    @classmethod
    def name_validator(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or len(v) > 50:
            raise ValidationError("invalid_permission_name")
        return v.strip()

    @field_validator("resource")
    @classmethod
    def resource_validator(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or len(v) > 30:
            raise ValidationError("invalid_resource")
        return v.strip()

    @field_validator("action")
    @classmethod
    def action_validator(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or len(v) > 20:
            raise ValidationError("invalid_action")
        return v.strip()


class PermissionPublic(PermissionBase):
    id: int

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class RoleBase(BaseModel):
    name: RoleEnum
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_validator(cls, v: RoleEnum) -> RoleEnum:
        try:
            return RoleEnum(v)
        except ValueError:
            raise ValidationError("invalid_role")


class RoleCreate(RoleBase):
    permissions: list[str] | None = None


class RoleUpdate(BaseModel):
    name: RoleEnum | None = None
    description: str | None = None
    permissions: list[str] | None = None

    @field_validator("name")
    @classmethod
    def name_validator(cls, v: RoleEnum | None) -> RoleEnum | None:
        if v is None:
            return v
        try:
            return RoleEnum(v)
        except ValueError:
            raise ValidationError("invalid_role")


class RolePublic(RoleBase):
    id: int
    permissions: list[PermissionPublic] = []

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

    @field_validator("permissions", mode="before")
    @classmethod
    def permissions_from_obj(cls, v: Any) -> list[PermissionPublic]:
        if isinstance(v, list):
            result = []
            for item in v:
                if isinstance(item, Permission):
                    result.append(PermissionPublic.model_validate(item))
                elif isinstance(item, dict):
                    result.append(PermissionPublic(**item))
                elif isinstance(item, PermissionPublic):
                    result.append(item)
            return result
        return []

    def permission_names(self) -> list[str]:
        return [p.name for p in self.permissions]


class RoleWithUsers(RolePublic):
    user_count: int = 0


class AssignRoleRequest(BaseModel):
    user_id: str
    role_id: int


class AssignPermissionsRequest(BaseModel):
    role_id: int
    permission_ids: list[int]
