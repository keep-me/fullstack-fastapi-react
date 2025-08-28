"""
Session repository for the application.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.domain.session import Session
from app.models.schemas.session import SessionCreate, SessionUpdate
from app.repositories.base import BaseRepository

logger = logging.getLogger("app.repositories.session")


class SessionRepository(BaseRepository[Session, SessionCreate, SessionUpdate]):
    """
    Session repository for managing user sessions.
    """

    def __init__(self) -> None:
        """
        Initialize the session repository.
        """
        super().__init__(Session)

    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> list[Session]:
        """
        Get sessions by user ID.
        """
        logger.debug(f"Getting sessions for user: {user_id}")
        return await self.get_multi(
            session=session,
            skip=0,
            limit=100,
            filters={"user_id": user_id},
        )

    async def get_by_refresh_token(
        self,
        session: AsyncSession,
        refresh_token: str,
    ) -> Session | None:
        """
        Get session by refresh token.
        """
        logger.debug("Getting session by refresh token")
        result = await session.execute(
            select(Session).where(Session.refresh_token == refresh_token),
        )
        return result.scalar_one_or_none()

    async def delete_by_refresh_token(
        self,
        session: AsyncSession,
        refresh_token: str,
    ) -> bool:
        """
        Delete session by refresh token.
        """
        logger.debug("Deleting session by refresh token")
        result = await session.execute(
            delete(Session)
            .where(Session.refresh_token == refresh_token)
            .returning(Session.id),
        )
        deleted = result.first() is not None

        if deleted:
            logger.info("Session deleted successfully")
        else:
            logger.warning("Session not found for deletion")

        return deleted

    async def create_or_update_session(
        self,
        session: AsyncSession,
        user_id: UUID,
        refresh_token: str,
        fingerprint: str,
    ) -> Session:
        """
        Create or update session.
        """
        logger.debug(f"Creating or updating session for user: {user_id}")
        user_sessions = await self.get_by_user_id(session, user_id)
        matching_session = next(
            (s for s in user_sessions if s.fingerprint == fingerprint),
            None,
        )

        expires_at = (
            datetime.now().astimezone() + settings.REFRESH_TOKEN_EXPIRE
        ).isoformat()

        if matching_session:
            logger.debug("Updating existing session with matching fingerprint")
            new_session = matching_session
        elif len(user_sessions) >= settings.MAX_REFRESH_SESSIONS:
            logger.info(
                f"User has reached max sessions ({settings.MAX_REFRESH_SESSIONS}), replacing oldest",
            )
            new_session = min(
                user_sessions,
                key=lambda x: datetime.fromisoformat(x.expires_at)
                if x.expires_at
                else datetime.min,
            )
            new_session.fingerprint = fingerprint
        else:
            logger.debug("Creating new session")
            session_data = SessionCreate(
                user_id=user_id,
                fingerprint=fingerprint,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
            new_session = await self.create(session=session, obj_in=session_data)
            return new_session

        update_data = SessionUpdate(
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        new_session = await self.update(
            session=session,
            db_obj=new_session,
            obj_in=update_data,
        )
        return new_session


session_repo = SessionRepository()
