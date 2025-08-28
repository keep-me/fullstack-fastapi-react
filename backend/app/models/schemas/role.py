from pydantic import BaseModel

from app.models.domain.role import RoleEnum


class RoleCreate(BaseModel):
    """
    Schema for creating a role
    """

    name: RoleEnum
    description: str | None = None


class RoleUpdate(BaseModel):
    """
    Schema for updating a role
    """

    name: RoleEnum | None = None
    description: str | None = None
