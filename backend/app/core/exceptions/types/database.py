"""
Database exception types for the application.
"""

from fastapi import status

from app.core.exceptions.types.base import HTTPException


class DatabaseError(HTTPException):
    """
    Exception for handling database operation errors.
    """

    def __init__(self, error_type: str, details: str = None) -> None:
        message = "Database error"
        error = "Database operation failed"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        match error_type:
            case "connection_failed":
                message = "Database connection failed. Please try again later."
                error = "Unable to connect to database"
            case "query_failed":
                message = "Database query failed. Please try again later."
                error = details or "SQL query execution failed"
            case "transaction_failed":
                message = "Database transaction failed. Please try again later."
                error = details or "Transaction could not be completed"
            case "integrity_error_username":
                status_code = status.HTTP_409_CONFLICT
                message = "User with this username already exists."
                error = "username_exists"
            case "integrity_error_email":
                status_code = status.HTTP_409_CONFLICT
                message = "User with this email already exists."
                error = "email_exists"
            case "timeout":
                message = "Database operation timed out. Please try again later."
                error = "Database operation timeout"
            case "lock_error":
                message = "Database lock error. Please try again later."
                error = "Database resource is locked"
            case "create_database_failed":
                message = "Failed to create database. Please check your configuration."
                error = "Database creation failed"

        super().__init__(
            status_code=status_code,
            message=message,
            error=error,
        )
