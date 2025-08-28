from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.core.exceptions import ValidationError
from app.models.domain.role import Role, RoleEnum
from app.validators.user import EmailValidator, PasswordValidator, UsernameValidator


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str | None = None

    @field_validator("username")
    @classmethod
    def username_validator(cls, v: str) -> str:
        return UsernameValidator.validate(v.lower().strip())

    @field_validator("email")
    @classmethod
    def email_validator(cls, v: str) -> str:
        return EmailValidator.validate(v.lower().strip())


class UserPublic(UserBase):
    id: UUID
    is_active: bool = True
    role: RoleEnum | None = None

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

    @field_validator("role", mode="before")
    @classmethod
    def role_from_obj(cls, v: Any) -> RoleEnum | str | None:
        if isinstance(v, Role):
            return v.name
        if isinstance(v, RoleEnum):
            return v
        if isinstance(v, str):
            return v
        return None

    def role_name(self) -> str | None:
        return self.role.value if self.role else None


class UserRegister(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: str) -> str:
        return PasswordValidator.validate(v.strip())


class UserCreate(UserRegister):
    role: RoleEnum = RoleEnum.USER

    @field_validator("role")
    @classmethod
    def role_validator(cls, v: RoleEnum) -> RoleEnum:
        try:
            return RoleEnum(v)
        except ValueError:
            raise ValidationError("invalid_role")

    is_active: bool = True


class UserLogin(BaseModel):
    username: str
    password: str
    fingerprint: str

    @field_validator("username")
    @classmethod
    def username_validator(cls, v: str) -> str:
        return UsernameValidator.validate(v.lower().strip())

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: str) -> str:
        return PasswordValidator.validate(v.strip())


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None
    full_name: str | None = None
    role: RoleEnum | None = None
    is_active: bool | None = None

    @field_validator("role")
    @classmethod
    def role_validator(cls, v: RoleEnum | None) -> RoleEnum | None:
        if v is None:
            return v
        try:
            return RoleEnum(v)
        except ValueError:
            raise ValidationError("invalid_role")

    @field_validator("username")
    @classmethod
    def username_validator(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return UsernameValidator.validate(v.lower())

    @field_validator("email")
    @classmethod
    def email_validator(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return EmailValidator.validate(v.lower().strip())

    @field_validator("password")
    @classmethod
    def password_validator(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return PasswordValidator.validate(v.strip())


class UpdatePassword(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_validator(cls, v: str) -> str:
        return PasswordValidator.validate(v.strip())

    @field_validator("current_password")
    @classmethod
    def current_password_validator(cls, v: str) -> str:
        return PasswordValidator.validate(v.strip())
