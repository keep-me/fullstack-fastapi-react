"""
Token exception types for the application.
"""

from fastapi import status

from app.core.exceptions.types.base import HTTPException


class TokenError(HTTPException):
    """
    Exception for handling authentication token errors.
    """

    def __init__(self, error_type: str, expected_type: str = None) -> None:
        message = "Access error. Please, try again later."
        error = "Unknown refresh token error"
        status_code = status.HTTP_401_UNAUTHORIZED

        match error_type:
            case "not_found":
                error = "Token not found in request"
            case "invalid_token":
                error = "Invalid token"
            case "invalid_token_type":
                error = "Invalid token type"
            case "token_expired":
                message = "Verification error."
                error = "Token has expired"
            case "invalid_user_id":
                error = "Token does not contain user_id"
            case "no_session":
                error = "No session found with this refresh token"
            case "invalid_ownership":
                error = "Invalid session ownership"
            case "missing_access_token":
                error = "Access token is required for token refresh"
            case "invalid_access_token":
                error = "Invalid access token"
            case "invalid_refresh_token":
                error = "Invalid refresh token"
            case "token_mismatch":
                error = "Access token and refresh token do not match"
            case "user_not_found":
                error = "User not found"
            case "not_verified":
                error = "Code is invalid or expired"

        super().__init__(
            status_code=status_code,
            message=message,
            error=error,
        )
