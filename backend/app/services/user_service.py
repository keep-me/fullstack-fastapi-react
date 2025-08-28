"""
User service for the application.
"""

from uuid import UUID

from app.core.exceptions import (
    UserAccessError,
    ValidationError,
)
from app.models.domain.user import User
from app.models.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserUpdate,
)
from app.repositories.unit_of_work import UnitOfWork
from app.validators.user import PasswordValidator


class UserService:
    """
    Service for handling user-related business logic.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_user(
        self,
        user_in: UserCreate,
    ) -> UserPublic:
        """
        Create a new user with validation.
        """
        db_user = await self.uow.users.get_user(
            session=self.uow.session,
            username=user_in.username,
            email=user_in.email,
        )

        if db_user:
            if db_user.username == user_in.username.lower():
                raise ValidationError("username_exists")
            if db_user.email == user_in.email.lower():
                raise ValidationError("email_exists")

        new_user = await self.uow.users.create_user(
            session=self.uow.session,
            obj_in=user_in,
        )
        return UserPublic.model_validate(new_user)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[UserPublic]:
        """
        Get list of active users with pagination.
        """
        result = await self.uow.users.get_users(
            session=self.uow.session,
            skip=skip,
            limit=limit,
        )
        return [UserPublic.model_validate(user) for user in result]

    async def update_user_me(
        self,
        current_user: User,
        user_in: UserUpdate,
    ) -> UserPublic:
        """
        Update current user's information with validation.
        """
        update_data = user_in.model_dump(exclude_unset=True)
        if not update_data:
            raise ValidationError("empty_data")

        username = update_data.get("username")
        email = update_data.get("email")
        if username or email:
            db_user = await self.uow.users.get_user(
                session=self.uow.session,
                username=username,
                email=email,
            )
            if db_user and db_user.id != current_user.id:
                if username and db_user.username == username.lower():
                    raise ValidationError("username_exists")
                if email and db_user.email == email.lower():
                    raise ValidationError("email_exists")

        updated_user = await self.uow.users.update_user(
            session=self.uow.session,
            current_user=current_user,
            obj_in=user_in,
        )

        return UserPublic.model_validate(updated_user)

    async def update_password_me(
        self,
        current_user: User,
        password_update: UpdatePassword,
    ) -> None:
        """
        Update current user's password.
        """
        new_password = PasswordValidator.validate_update(
            password_update.current_password,
            password_update.new_password,
            current_user.hashed_password,
        )

        await self.uow.users.update_password(
            session=self.uow.session,
            user=current_user,
            new_password=new_password,
        )

    async def delete_user_me(self, current_user: User) -> None:
        """
        Delete current user account.
        """
        if current_user.is_admin:
            raise UserAccessError("self_delete")

        await self.uow.users.delete_user(session=self.uow.session, user=current_user)

    async def get_user_by_id(self, user_id: UUID) -> UserPublic:
        """
        Get user by ID with role information.
        """
        db_user = await self.uow.users.get_by_user_id(
            session=self.uow.session,
            user_id=user_id,
        )
        if not db_user:
            raise UserAccessError("user_not_found")

        return UserPublic.model_validate(db_user)

    async def update_user(
        self,
        current_user: User,
        user_id: UUID,
        user_in: UserUpdate,
    ) -> UserPublic:
        """
        Update user by admin with validation.
        """
        if current_user.id == user_id:
            db_user = current_user
        else:
            user = await self.uow.users.get_by_user_id(
                session=self.uow.session,
                user_id=user_id,
            )
            if not user:
                raise UserAccessError("user_not_found")
            db_user = user

        update_data = user_in.model_dump(exclude_unset=True)
        username = update_data.get("username")
        email = update_data.get("email")

        if username or email:
            conflict_user = await self.uow.users.get_user(
                session=self.uow.session,
                username=username,
                email=email,
            )
            if conflict_user and conflict_user.id != db_user.id:
                if username and conflict_user.username == username.lower():
                    raise ValidationError("username_exists")
                if email and conflict_user.email == email.lower():
                    raise ValidationError("email_exists")

        if user_in.password:
            PasswordValidator.validate(user_in.password)

        updated_user = await self.uow.users.update_user(
            session=self.uow.session,
            current_user=db_user,
            obj_in=user_in,
        )

        return UserPublic.model_validate(updated_user)

    async def delete_user_by_id(self, user_id: UUID) -> UserPublic:
        """
        Delete user by ID.
        """
        user = await self.uow.users.get_by_user_id(
            session=self.uow.session,
            user_id=user_id,
        )
        if not user:
            raise UserAccessError("user_not_found")

        user_public = UserPublic.model_validate(user)
        await self.uow.users.delete_user(session=self.uow.session, user=user)
        return user_public
