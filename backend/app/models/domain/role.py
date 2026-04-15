import enum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.domain.permission import role_permission

if TYPE_CHECKING:
    from app.models.domain.permission import Permission
    from app.models.domain.user import User


class RoleEnum(str, enum.Enum):
    """
    Enum for user roles
    """

    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"
    GUEST = "GUEST"


class Role(Base):
    """
    Role model for user permissions
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=role_permission,
        back_populates="roles",
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def __str__(self) -> str:
        return self.name

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if the role has a specific permission.
        """
        return any(perm.name == permission_name for perm in self.permissions)

    def get_permission_names(self) -> list[str]:
        """
        Get all permission names for this role.
        """
        return [perm.name for perm in self.permissions]
