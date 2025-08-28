import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.domain.user import User


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {"extend_existing": True}

    id: Mapped[uuid.UUID] = Column(  # type: ignore[misc]
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = Column(  # type: ignore[misc]
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    refresh_token: Mapped[str] = Column(String, nullable=False, index=True)
    expires_at: Mapped[str] = Column(String, nullable=False)
    fingerprint: Mapped[str] = Column(String, nullable=False)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
        lazy="joined",
    )
