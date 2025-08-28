from pydantic import BaseModel, field_validator

from app.validators.user import EmailValidator, PasswordValidator


class PasswordResetRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v: str) -> str:
        return EmailValidator.validate(v.lower().strip())


class VerificationCode(BaseModel):
    code: str


class NewPassword(BaseModel):
    new_password: str
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_validator(cls, v: str) -> str:
        if v is None:
            return v
        return PasswordValidator.validate(v.strip())
