import enum
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
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

    def __repr__(self) -> str:
        return f"<Role {self.name}>"

    def __str__(self) -> str:
        return self.name
