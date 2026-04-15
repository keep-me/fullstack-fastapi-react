"""
Validation exception types for the application.
"""

from fastapi import status

from app.core.exceptions.types.base import HTTPException


class ValidationError(HTTPException):
    """
    Exception for handling user input data validation errors.
    """

    def __init__(self, error_type: str) -> None:
        message = "Validation error"
        error = "Validation error"

        match error_type:
            case "username_exists":
                message = "User with this username already exists"
            case "email_exists":
                message = "User with this email already exists"
            case "invalid_username":
                message = "Username must be at least 3 characters long and contain only letters and numbers."
            case "invalid_email":
                message = "Please, check your email and try again."
            case "invalid_password":
                message = "Password must be at least 8 characters long."
            case "incorrect_password":
                message = "Incorrect password"
                error = "Password is incorrect"
            case "password_not_set":
                message = "Password (hashed) is not set"
            case "same_password":
                message = "New password cannot be the same as the current password"
            case "passwords_not_match":
                message = "Passwords do not match"
            case "empty_data":
                message = "Please, check your data and try again."
            case "invalid_role":
                message = (
                    "Invalid role. Role must be one of: ADMIN, MANAGER, USER, GUEST."
                )
            case "invalid_uuid":
                message = "Invalid user ID format. Please provide a valid UUID."
                error = "Invalid UUID format"
            case "invalid_pagination":
                message = "Pagination parameters must be greater than 0."
                error = "Invalid pagination parameters"
            case "role_not_found":
                message = "Role not found"
                error = "The specified role does not exist"
            case "role_exists":
                message = "Role already exists"
                error = "A role with this name already exists"
            case "permission_not_found":
                message = "Permission not found"
                error = "The specified permission does not exist"
            case "permission_exists":
                message = "Permission already exists"
                error = "A permission with this name already exists"
            case "role_or_permission_not_found":
                message = "Role or permission not found"
                error = "The specified role or permission does not exist"
            case "invalid_permission_name":
                message = "Invalid permission name"
                error = "Permission name must be between 1 and 50 characters"
            case "invalid_resource":
                message = "Invalid resource"
                error = "Resource must be between 1 and 30 characters"
            case "invalid_action":
                message = "Invalid action"
                error = "Action must be between 1 and 20 characters"

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            error=error,
        )
