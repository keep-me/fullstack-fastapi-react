"""
User exception types for the application.
"""

from fastapi import status

from app.core.exceptions.types.base import HTTPException


class UserAccessError(HTTPException):
    """
    Exception for handling user authentication and authorization errors.
    """

    def __init__(self, error_type: str) -> None:
        status_code = status.HTTP_400_BAD_REQUEST
        message = "Access error. Please, try again later."
        error = "Unknown user access error"

        match error_type:
            case "inactive":
                message = "Access error."
                error = "Inactive user. User has been deleted."
            case "not_admin":
                status_code = status.HTTP_403_FORBIDDEN
                message = "Access error."
                error = "The user doesn't have enough privileges."
            case "user_not_found":
                status_code = status.HTTP_404_NOT_FOUND
                message = "User not found."
                error = "User does not exist."
            case "self_delete":
                status_code = status.HTTP_403_FORBIDDEN
                message = "Admin cannot delete themselves"
                error = "Self-deletion is not allowed for admin users"
            case "invalid_username":
                message = "Invalid username."
                error = "Username is invalid or empty."
            case "role_has_users":
                status_code = status.HTTP_400_BAD_REQUEST
                message = "Cannot delete role."
                error = "Role has users assigned. Please reassign users first."
            case "insufficient_permissions":
                status_code = status.HTTP_403_FORBIDDEN
                message = "Access denied."
                error = "Insufficient permissions to perform this action."

        super().__init__(
            status_code=status_code,
            message=message,
            error=error,
        )
