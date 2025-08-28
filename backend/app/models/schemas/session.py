from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionBase(BaseModel):
    user_id: UUID
    fingerprint: str
    refresh_token: str | None = None
    expires_at: str | None = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    fingerprint: str | None = None
    refresh_token: str | None = None
    expires_at: str | None = None


class SessionInDB(SessionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
