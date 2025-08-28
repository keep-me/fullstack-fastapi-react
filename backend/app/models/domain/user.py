import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.domain.role import Role, RoleEnum

if TYPE_CHECKING:
    from app.models.domain.session import Session


class User(Base):
    """
    User model for authentication and authorization
    """

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = Column(  # type: ignore[misc]
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="joined")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="user")

    @property
    def is_admin(self) -> bool:
        return self.role is not None and self.role.name == RoleEnum.ADMIN

    def __repr__(self) -> str:
        return f"<User {self.username}>"
