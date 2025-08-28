"""
User validator for the application.
"""

import re

from email_validator import (
    EmailNotValidError,
    EmailSyntaxError,
    ValidatedEmail,
    validate_email,
)

from app.core.exceptions import ValidationError


class UsernameValidator:
    """
    Validator for username format and constraints.
    """

    @classmethod
    def validate(cls, username: str) -> str:
        """
        Validate username format and length.
        """
        if not (3 <= len(username) <= 20):
            raise ValidationError("invalid_username")

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            raise ValidationError("invalid_username")

        return username


class EmailValidator:
    """
    Validator for email format and syntax.
    """

    @classmethod
    def validate(cls, email: str) -> str:
        """
        Validate email format and normalize it.
        """
        try:
            validated_email: ValidatedEmail = validate_email(
                email,
                check_deliverability=False,
            )
            return validated_email.normalized
        except (EmailNotValidError, EmailSyntaxError):
            raise ValidationError("invalid_email")


class PasswordValidator:
    """
    Validator for password requirements and updates.
    """

    @classmethod
    def validate(cls, password: str) -> str:
        """
        Validate password length and complexity.
        """
        if len(password) < 8:
            raise ValidationError("invalid_password")
        return password

    @classmethod
    def validate_update(
        cls,
        current_password: str,
        new_password: str,
        hashed_current: str,
    ) -> str:
        """
        Validate password update with current password verification.
        """
        from app.utils.password import verify_password

        if not hashed_current:
            raise ValidationError("password_not_set")

        if not verify_password(current_password, hashed_current):
            raise ValidationError("incorrect_password")

        if current_password == new_password:
            raise ValidationError("same_password")

        return cls.validate(new_password)
