import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.domain.role import Role


class PermissionEnum(str, enum.Enum):
    """
    Enum for permission names.
    """

    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    ROLE_READ = "role:read"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"

    PERMISSION_READ = "permission:read"
    PERMISSION_CREATE = "permission:create"
    PERMISSION_UPDATE = "permission:update"
    PERMISSION_DELETE = "permission:delete"

    ENDPOINT_EXECUTE = "endpoint:execute"
    ENDPOINT_MANAGE = "endpoint:manage"


role_permission = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
    UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
)


class Permission(Base):
    """
    Permission model for defining access control permissions.
    """

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resource: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permission,
        back_populates="permissions",
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"

    def __str__(self) -> str:
        return self.name
