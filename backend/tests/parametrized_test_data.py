from unittest.mock import Mock
from uuid import uuid4

from fastapi import Request, status
from pytest_lazy_fixtures import lf
from redis.exceptions import (
    ConnectionError,
    ResponseError,
    TimeoutError,
)

from app.core.exceptions.types import (
    DatabaseError,
    TokenError,
    UserAccessError,
    ValidationError,
)
from app.models.domain.role import Role, RoleEnum
from app.utils.notification import (
    send_delete_user_email,
    send_password_changed_email,
    send_password_reset_email,
    send_welcome_email,
)
from app.utils.password import (
    get_password_hash_async,
    get_password_hash_fast,
    get_password_hash_fast_async,
)
from tests.utils import _TestCreateSchema, _TestModel, _TestUpdateSchema

# fmt: off
register_user_param_data = [
        (lf("random_user_data"), None, None, status.HTTP_201_CREATED, None),
        ({"username": ""}, ValidationError, "invalid_username", status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ({"username": lf("test_user_username")}, ValidationError, "username_exists", status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this username already exists"),
        ({"email": ""}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"email": "invalid-email"}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"email": lf("test_user_email")}, ValidationError, "email_exists", status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this email already exists"),
        ({"password": ""}, ValidationError, "invalid_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
    ]

login_user_param_data = [
        (lf("test_user_username"), "Password123", "test_fingerprint", None, None, status.HTTP_200_OK, None),
        ("nonexistent_user", "Password123", "test_fingerprint", UserAccessError, "user_not_found", status.HTTP_404_NOT_FOUND, "User not found."),
        (lf("test_user_username"), "wrongpassword", "test_fingerprint", ValidationError, "incorrect_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
        (lf("test_user_username_inactive"), "Password123", "test_fingerprint", UserAccessError, "inactive", status.HTTP_400_BAD_REQUEST, "Access error."),
        ("", "Password123", "test_fingerprint", UserAccessError, "invalid_username", status.HTTP_400_BAD_REQUEST, "Invalid username."),
        (lf("test_user_username"), "", "test_fingerprint", ValidationError, "incorrect_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
    ]

logout_user_param_data = [
        (lf("login_and_get_headers_test_user"), None, None, status.HTTP_200_OK, "Successfully logged out"),
        ({}, None, None, status.HTTP_200_OK, "Already logged out or no active session"),
        (None, None, None, status.HTTP_200_OK, "Already logged out or no active session"),
        ({"Authorization": "Bearer invalid_token"}, None, None, status.HTTP_200_OK, "Already logged out or no active session"),
    ]

refresh_token_param_data = [
        ("valid", "initial_fingerprint", None, None, status.HTTP_200_OK, None),
        ("no_cookie", "initial_fingerprint", TokenError, "no_session", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("invalid_cookie", "initial_fingerprint", TokenError, "invalid_token", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("valid", "wrong_fingerprint", TokenError, "invalid_ownership", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("no_header", "initial_fingerprint", TokenError, "no_session", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("invalid_header", "initial_fingerprint", TokenError, "invalid_token", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
    ]

reset_password_param_data = [
        (lf("test_user_email"), None, None, status.HTTP_200_OK, "Verification code sent"),
        ("nonexistent@example.com", UserAccessError, "user_not_found", status.HTTP_404_NOT_FOUND, "User not found."),
        (lf("test_user_email_inactive"), UserAccessError, "inactive", status.HTTP_400_BAD_REQUEST, "Access error."),
    ]

verify_code_param_data = [
        ("123456", None, None, status.HTTP_200_OK, "Code verified successfully"),
        ("000000", TokenError, "not_verified", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("", TokenError, "not_verified", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
    ]

set_new_password_param_data = [
        ("NewPassword123", "NewPassword123", None, None, status.HTTP_200_OK, "Password changed successfully"),
        ("NewPassword123", "DifferentPassword123", ValidationError, "passwords_not_match", status.HTTP_422_UNPROCESSABLE_ENTITY, "Passwords do not match"),
        ("NewPassword123", "NewPassword123", TokenError, "invalid_refresh_token", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("", "", TokenError, "invalid_refresh_token", status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
    ]

create_user_param_data = [
        (lf("login_and_get_headers_test_superuser"), status.HTTP_201_CREATED, None, None, None, {"role": RoleEnum.USER, "full_name": "Test User"}),
        (lf("login_and_get_headers_test_user"), status.HTTP_403_FORBIDDEN, UserAccessError, "not_admin", "Access error.", {}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_username", "Username must be at least 3 characters long and contain only letters and numbers.", {"username": ""}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_username", "Username must be at least 3 characters long and contain only letters and numbers.", {"username": None}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_username", "Username must be at least 3 characters long and contain only letters and numbers.", {"username": "ab"}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_username", "Username must be at least 3 characters long and contain only letters and numbers.", {"username": "a" * 21}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_username", "Username must be at least 3 characters long and contain only letters and numbers.", {"username": "user@name"}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_email", "Please, check your email and try again.", {"email": ""}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_email", "Please, check your email and try again.", {"email": None}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_email", "Please, check your email and try again.", {"email": "invalid-email"}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_email", "Please, check your email and try again.", {"email": "@example.com"}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_email", "Please, check your email and try again.", {"email": "test@"}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_password", "Password must be at least 8 characters long.", {"password": ""}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_password", "Password must be at least 8 characters long.", {"password": None}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "invalid_password", "Password must be at least 8 characters long.", {"password": "1234567"}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_201_CREATED, None, None, None, {"role": RoleEnum.ADMIN}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_201_CREATED, None, None, None, {"role": RoleEnum.USER}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_201_CREATED, None, None, None, {"is_active": True}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_201_CREATED, None, None, None, {"is_active": False}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_201_CREATED, None, None, None, {"full_name": ""}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_201_CREATED, None, None, None, {"full_name": "A" * 100}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "username_exists", "User with this username already exists", {"username": lf("test_user_username")}),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_422_UNPROCESSABLE_ENTITY, ValidationError, "email_exists", "User with this email already exists", {"email": lf("test_user_email")}),
    ]

get_users_param_data = [
        (lf("login_and_get_headers_test_superuser"), status.HTTP_200_OK, None, None, None),
        (lf("login_and_get_headers_test_user"), status.HTTP_403_FORBIDDEN, UserAccessError, "not_admin", "Access error."),
    ]

update_user_me_param_data = [
        ({"username": "newusername"}, None, None, status.HTTP_200_OK, None),
        ({"username": lf("test_superuser_username")}, ValidationError, "username_exists", status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this username already exists"),
        ({"username": "ab"}, ValidationError, "invalid_username", status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ({"username": ""}, ValidationError, "invalid_username", status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ({"username": "a" * 21}, ValidationError, "invalid_username", status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ({"username": "user@name"}, ValidationError, "invalid_username", status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ({"email": "newemail@example.com"}, None, None, status.HTTP_200_OK, None),
        ({"email": lf("test_superuser_email")}, ValidationError, "email_exists", status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this email already exists"),
        ({"email": "invalid-email"}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"email": ""}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"email": "@example.com"}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"email": "test@"}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"full_name": "New Full Name"}, None, None, status.HTTP_200_OK, None),
        ({"full_name": ""}, None, None, status.HTTP_200_OK, None),
        ({"full_name": "A" * 100}, None, None, status.HTTP_200_OK, None),

    ]

update_password_me_param_data = [
        ({"current_password": "Password123", "new_password": "NewPassword123"}, None, None, status.HTTP_200_OK, "Password updated successfully"),
        ({"current_password": "Password123", "new_password": ""}, ValidationError, "invalid_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
        ({"current_password": "Password123", "new_password": "1234567"}, ValidationError, "invalid_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
        ({"current_password": "Password123", "new_password": "Password123"}, ValidationError, "same_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "New password cannot be the same as the current password"),
        ({"current_password": "wrongpassword", "new_password": "NewPassword123"}, ValidationError, "incorrect_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
        ({"current_password": "", "new_password": "NewPassword123"}, ValidationError, "incorrect_password", status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
    ]

delete_user_me_param_data = [
        (lf("login_and_get_headers_test_user"), status.HTTP_200_OK, None, None, "User deleted successfully"),
        (lf("login_and_get_headers_test_superuser"), status.HTTP_403_FORBIDDEN, UserAccessError, "self_delete", "Admin cannot delete themselves"),
    ]

get_user_by_id_param_data = [
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_user"), lf("test_user_id"), UserAccessError, "not_admin", status.HTTP_403_FORBIDDEN, "Access error."),
        (lf("login_and_get_headers_test_superuser"), str(uuid4()), UserAccessError, "user_not_found", status.HTTP_404_NOT_FOUND, "User not found."),
    ]

update_user_by_id_param_data = [
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"username": "newusername"}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"username": ""}, ValidationError, "invalid_username", status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"email": "newemail@example.com"}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"email": ""}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"email": "invalid-email"}, ValidationError, "invalid_email", status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"full_name": "New Full Name"}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"is_active": False}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"is_active": True}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"role": RoleEnum.USER}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"role": RoleEnum.ADMIN}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"role": "invalid_role"}, ValidationError, "invalid_role", status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid role. Role must be one of: ADMIN, MANAGER, USER, GUEST."),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"password": "NewPassword123"}, None, None, status.HTTP_200_OK, None),
        (lf("login_and_get_headers_test_user"), lf("test_user_id"), {"username": "newusername"}, UserAccessError, "not_admin", status.HTTP_403_FORBIDDEN, "Access error."),
        (lf("login_and_get_headers_test_superuser"), str(uuid4()), {"username": "newusername"}, UserAccessError, "user_not_found", status.HTTP_404_NOT_FOUND, "User not found."),
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), {"username": lf("test_superuser_username")}, ValidationError, "username_exists", status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this username already exists"),
    ]

delete_user_by_id_param_data = [
        (lf("login_and_get_headers_test_superuser"), lf("test_user_id"), None, None, status.HTTP_200_OK, "User deleted successfully"),
        (lf("login_and_get_headers_test_user"), lf("test_user_id"), UserAccessError, "not_admin", status.HTTP_403_FORBIDDEN, "Access error."),
        (lf("login_and_get_headers_test_superuser"), str(uuid4()), UserAccessError, "user_not_found", status.HTTP_404_NOT_FOUND, "User not found."),
    ]

handle_email_message_smtp_failure_param_data = [
        {"hostname": None}, {"hostname": ""},
        {"port": 0},
        {"username": None}, {"username": ""},
        {"password": None}, {"password": ""},
    ]

limiter_param_data = [
        ({"X-Forwarded-For": "1.1.1.1, 2.2.2.2"}, "1.1.1.1"),
        ({"X-Forwarded-For": "192.168.1.1"}, "192.168.1.1"),
        ({"X-Real-IP": "10.0.0.1"}, "10.0.0.1"),
        ({}, "127.0.0.1"),
        ({"X-Forwarded-For": "bad-ip"}, "bad-ip"),
        ({"X-Forwarded-For": " 10.0.0.1 "}, "10.0.0.1"),
    ]

redis_error_param_data = [
        ("invalid_host", 6379, 0, 1, ConnectionError),
        ("localhost", 9999, 0, 1, ConnectionError),
        ("localhost", 6379, 100, 1, ResponseError),
        ("localhost", 6379, 0, 0.00001, TimeoutError),
    ]

get_by_refresh_token_param_data = [
        ("non-existent-token", None),
        (None, None),
    ]

remove_session_param_data = [
        ("non-existent-token", False),
        (None, True),
    ]

repo_get_by_id_param_data = [
        (_TestModel(id=uuid4(), name="test"), None, "model", None, None, None),
        (None, None, None, None, None, None),
        (None, DatabaseError("query_failed", "DB Error"), None, DatabaseError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database query failed. Please try again later."),
    ]

repo_get_multi_param_data = [
        (None, None, [_TestModel(id=uuid4(), name=f"test_{i}") for i in range(3)], None, None, None, None),
        (10, 5, [_TestModel(id=uuid4(), name="test")], None, None, None, None),
        (None, None, None, DatabaseError("query_failed", "DB Error"), DatabaseError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database query failed. Please try again later."),
    ]

repo_create_param_data = [
        (_TestCreateSchema(name="test"), _TestModel(id=uuid4(), name="test"), None, None, None, None),
        (_TestCreateSchema(name="test", password="password123"), _TestModel(id=uuid4(), name="test", hashed_password="hashed"),None, None, None, None),
        (_TestCreateSchema(name="test"), None, DatabaseError("integrity_error", "Integrity constraint failed"), DatabaseError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error"),
        (_TestCreateSchema(name="test"), None, DatabaseError("query_failed", "DB Error"), DatabaseError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database query failed. Please try again later."),
    ]

repo_update_param_data = [
        (_TestModel(id=uuid4(), name="old_name"), _TestUpdateSchema(name="new_name"), _TestModel(id=uuid4(), name="new_name"), None, None, None, None),
        (_TestModel(id=uuid4(), name="old_name"), _TestUpdateSchema(name="new_name"), None, DatabaseError("integrity_error", "Integrity constraint failed"), DatabaseError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database error"),
        (_TestModel(id=uuid4(), name="old_name"), _TestUpdateSchema(name="new_name"), None, DatabaseError("query_failed", "DB Error"), DatabaseError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database query failed. Please try again later."),
    ]

repo_delete_param_data = [
        (_TestModel(id=uuid4(), name="test"), None, None, None, None),
        (None, DatabaseError("query_failed", "DB Error"), DatabaseError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Database query failed. Please try again later."),
    ]

repo_get_by_user_id_param_data = [
        (lf("test_user_id"), True),
        (uuid4(), False),
    ]

repo_get_user_param_data = [
        ("username", lf("test_user"), True),
        ("email", lf("test_user"), True),
        ("username", "nonexistent", False),
    ]

repo_create_user_param_data = [
        (lf("random_user_data"), None, None, None, None),
        (lf("random_user_data"), "username", DatabaseError, status.HTTP_409_CONFLICT, "User with this username already exists."),
        (lf("random_user_data"), "email", DatabaseError, status.HTTP_409_CONFLICT, "User with this email already exists."),
    ]

repo_update_user = [
        ({"username": "upd_username"}),
        ({"email": "upd_email@example.com"}),
        ({"full_name": "Upd FullName"}),
    ]

repo_get_users_pagination_param_data = [
        ({"skip": 0, "limit": 2}, 2),
        ({"skip": 2, "limit": 2}, 2),
        ({"skip": 4, "limit": 2}, 1),
    ]

repo_get_by_name_param_data = [
        (RoleEnum.USER, Role(id=1, name=RoleEnum.USER, description="Regular user"), None, "found"),
        (RoleEnum.ADMIN, None, None, "not_found"),
        (RoleEnum.USER, None, DatabaseError("query_failed", "DB Error"), "database_error"),
    ]

repo_create_new_role_param_data = [
        (RoleEnum.ADMIN, "Administrator", None, "without_id"),
        (RoleEnum.ADMIN, "Administrator", 1, "with_id"),
    ]

repo_get_or_create_param_data = [
        (RoleEnum.USER, "Regular user", None, Role(id=1, name=RoleEnum.USER, description="Regular user"), "existing_role"),
        (RoleEnum.ADMIN, "Administrator", 2, None, "new_role"),
    ]

repo_role_enum_param_data = [
        (RoleEnum.ADMIN, "Administrator"),
        (RoleEnum.MANAGER, "Manager"),
        (RoleEnum.USER, "Regular user"),
        (RoleEnum.GUEST, "Guest user"),
    ]

authenticate_param_data = [
        (lf("test_user_username"), "Password123", True),
        (lf("test_user_username"), "wrongpassword", False),
        ("nonexistent", "Password123", False),
    ]

validate_token_param_data = [
        (lf("test_user_id"), "access", 0, False, "access", None, None, None),
        (lf("test_user_id"), "access", 30, True, "access", TokenError, status.HTTP_401_UNAUTHORIZED, "Token has expired"),
        (lf("test_user_id"), "access", 0, False, "refresh", TokenError, status.HTTP_401_UNAUTHORIZED, "Invalid token"),
    ]

auth_service_register_user_param_data = [
        ({"username": "newtestuser", "email": "newtestuser@example.com", "password": "Password123", "full_name": "New Test User"}, None, None, None),
        ({"username": lf("test_user_username"), "email": "another@example.com", "password": "Password123"}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this username already exists"),
        ({"username": "anotheruser", "email": lf("test_user_email"), "password": "Password123"}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this email already exists"),
    ]

auth_service_login_user_param_data = [
        (lf("test_user_username"), "Password123", None, None, None),
        ("nonexistent", "Password123", UserAccessError, status.HTTP_404_NOT_FOUND, "User not found."),
        (lf("test_user_username"), "WrongPassword123", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
        (lf("test_user_username_inactive"), "Password123", UserAccessError, status.HTTP_400_BAD_REQUEST, "Access error."),
        ("", "Password123", UserAccessError, status.HTTP_400_BAD_REQUEST, "Invalid username."),
        (lf("test_user_username"), "", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
    ]

auth_service_logout_param_data = [
        ("valid_token", "Successfully logged out", True),
        (None, "Already logged out or no active session", False),
        ("invalid_token", "Successfully logged out", False),
    ]

auth_service_refresh_token_param_data = [
        ("success", None, None, None),
        ("no_session", TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("no_auth_header", TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("invalid_auth_header", TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("no_refresh_cookie", TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
    ]

auth_service_request_reset_password_param_data = [
        (lf("test_user_email"), None, status.HTTP_200_OK, "Code sent successfully"),
        ("nonexistent@example.com", UserAccessError, status.HTTP_404_NOT_FOUND, "User not found."),
        (lf("test_user_email_inactive"), UserAccessError, status.HTTP_400_BAD_REQUEST, "Access error."),
    ]

auth_service_verify_code_param_data = [
        ("123456", None, status.HTTP_200_OK, "Code verified successfully"),
        ("wrong123", TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
    ]

auth_service_set_new_password_param_data = [
        ("NewPassword123", "NewPassword123", True, None, status.HTTP_200_OK, "Password changed successfully"),
        ("NewPassword123", "DifferentPassword123", True, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Passwords do not match"),
        ("NewPassword123", "NewPassword123", False, TokenError, status.HTTP_401_UNAUTHORIZED, "Verification error."),
    ]

user_service_create_user_param_data = [
        (lf("random_user_data"), None, None, None),
        ({"username": lf("test_user_username")}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this username already exists"),
        ({"username": ""}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ({"email": lf("test_user_email")}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this email already exists"),
        ({"email": ""}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"email": "invalid-email"}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"password": ""}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
    ]

user_service_update_user_me_param_data = [
        ({"username": "newusername"}, None, None, None),
        ({"username": lf("test_superuser_username")}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this username already exists"),
        ({"username": ""}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ({"email": "newemail@example.com"}, None, None, None),
        ({"email": lf("test_superuser_email")}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this email already exists"),
        ({"email": ""}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"email": "invalid-email"}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ({"full_name": "Updated Name"}, None, None, None),
        ({"full_name": ""}, None, None, None),
        ({}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your data and try again."),
    ]

user_service_update_password_me_param_data = [
        ("Password123", "NewPassword456", None, None, None),
        ("wrongpassword", "NewPassword456", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
        ("Password123", "Password123", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "New password cannot be the same as the current password"),
        ("Password123", "", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
        ("", "NewPassword456", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
    ]

user_service_delete_user_me_param_data = [
        (lf("test_user"), None, None, None),
        (lf("test_superuser"), UserAccessError, status.HTTP_403_FORBIDDEN, "Admin cannot delete themselves"),
    ]

user_service_get_user_by_id_param_data = [
        (lf("test_user_id"), None, None, None),
        (uuid4(), UserAccessError, status.HTTP_404_NOT_FOUND, "User not found."),
    ]

user_service_update_user_by_id_param_data = [
        (lf("test_user_id"), {"username": "updatedusername"}, None, None, None),
        (lf("test_user_id"), {"email": "updated@example.com"}, None, None, None),
        (lf("test_user_id"), {"password": "NewPassword123"}, None, None, None),
        (uuid4(), {"username": "test"}, UserAccessError, status.HTTP_404_NOT_FOUND, "User not found."),
        (lf("test_user_id"), {"username": lf("test_superuser_username")}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this username already exists"),
        (lf("test_user_id"), {"email": lf("test_superuser_email")}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "User with this email already exists"),
        (lf("test_user_id"), {"email": "invalid-email"}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        (lf("test_user_id"), {"email": ""}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        (lf("test_user_id"), {"full_name": ""}, None, None, None),
        (lf("test_user_id"), {"is_active": False}, None, None, None),
        (lf("test_user_id"), {"is_active": True}, None, None, None),
        (lf("test_user_id"), {"role": RoleEnum.USER}, None, None, None),
        (lf("test_user_id"), {"role": RoleEnum.ADMIN}, None, None, None),
        (lf("test_user_id"), {"password": "NewPassword123"}, None, None, None),
        (lf("test_user_id"), {"password": ""}, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
        (lf("test_user_id"), {"password": "Password123"}, None, None, None),
    ]

user_service_delete_user_by_id_param_data = [
        (lf("test_user_id"), None, None, None),
        (uuid4(), UserAccessError, status.HTTP_404_NOT_FOUND, "User not found."),
    ]

deps_validate_user_id_param_data = [
        (lf("test_user_id"), None, None, None),
        ("not-a-uuid", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid user ID format. Please provide a valid UUID."),
    ]

deps_get_current_user_param_data = [
        ("abc", lf("test_user_id"), True, True, None, None, None),
        (None, None, None, None, TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("abc", None, None, None, TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("abc", uuid4(), None, None, TokenError, status.HTTP_401_UNAUTHORIZED, "Access error. Please, try again later."),
        ("abc", lf("test_user_id_inactive"), True, False, UserAccessError, status.HTTP_400_BAD_REQUEST, "Access error."),
    ]

deps_get_current_active_user_param_data = [
        (True, None, None, None),
        (False, UserAccessError, status.HTTP_400_BAD_REQUEST, "Access error."),
    ]

deps_get_current_active_superuser_param_data = [
        (RoleEnum.ADMIN, None, None, None),
        (RoleEnum.USER, UserAccessError, status.HTTP_403_FORBIDDEN, "Access error."),
    ]

deps_pagination_params_param_data = [
        (0, 999, 100, None, None, None),
        (0, 10, 10, None, None, None),
        (-1, 10, 10, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Pagination parameters must be greater than 0."),
        (0, -1, 10, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Pagination parameters must be greater than 0."),
        (0, 0, 10, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Pagination parameters must be greater than 0."),
    ]

username_validator_param_data = [
        ("validuser", None, None, None),
        ("user123", None, None, None),
        ("valid_user", None, None, None),
        ("ab", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ("a" * 21, ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ("user-name", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ("user@name", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ("user name", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
        ("", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Username must be at least 3 characters long and contain only letters and numbers."),
    ]

email_validator_param_data = [
        ("test@example.com", None, None, None),
        ("user.name@domain.co.uk", None, None, None),
        ("user+tag@example.com", None, None, None),
        ("invalid-email", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ("@example.com", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ("test@", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ("test.example.com", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
        ("", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Please, check your email and try again."),
    ]

password_validator_param_data = [
        ("Password123", None, None, None),
        ("12345678", None, None, None),
        ("VeryLongPasswordWithSpecialChars!@#", None, None, None),
        ("1234567", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
        ("", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
    ]

password_update_validator_param_data = [
        ("CurrentPass123", "NewPass456", "hashed_current", None, None, None),
        ("WrongPass", "NewPass456", "hashed_current", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Incorrect password"),
        ("CurrentPass123", "CurrentPass123", "hashed_current", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "New password cannot be the same as the current password"),
        ("CurrentPass123", "Short", "hashed_current", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password must be at least 8 characters long."),
        ("CurrentPass123", "NewPass456", "", ValidationError, status.HTTP_422_UNPROCESSABLE_ENTITY, "Password (hashed) is not set"),
    ]

verify_password_param_data = [
        ("Password123", True),
        ("WrongPassword123", True),
        ("", True),
    ]

password_hashing_consistency_param_data = [
        (get_password_hash_async, True),
        (get_password_hash_fast, False),
        (get_password_hash_fast_async, True),
    ]

notification_sends_email_param_data = [
        (send_welcome_email, {"subject": "Welcome!", "body": "Hello, testuser! Welcome on a board!", "extra_data": None}),
        (send_password_changed_email, {"subject": "Password changed successfully", "body": "Hello, testuser! Your password has been changed successfully!", "extra_data": None}),
        (send_delete_user_email, {"subject": "Account deleted successfully", "body": "Hello, testuser! Your account has been deleted successfully!", "extra_data": None}),
        (send_password_reset_email, {"subject": "Password reset", "body": "Hello, testuser! Please use the following code to reset your password: 123456", "extra_data": "123456"}),
    ]

response_creation_param_data = [
        (
            {}, {
                "status_code": status.HTTP_200_OK,
                "success": True,
                "message": "Success",
                "has_data": False,
                "has_error": False,
                "request_id": None,
            },
        ),
        (
            {"data": {"id": 1, "name": "test"}, "message": "Data retrieved"},
            {
                "status_code": status.HTTP_200_OK,
                "success": True,
                "message": "Data retrieved",
                "has_data": True,
                "data": {"id": 1, "name": "test"},
                "has_error": False,
                "request_id": None,
            },
        ),
        (
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Bad request",
                "error": "Invalid input",
            },
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "success": False,
                "message": "Bad request",
                "has_data": False,
                "has_error": True,
                "error": "Invalid input",
                "request_id": None,
            },
        ),
    ]

response_with_request_id_param_data = [
        ("test-request-id-123", "test-request-id-123"),
        (None, None),
    ]

response_request_id_priority_param_data = [
        (None, {"request_id": "existing-id", "other": "data"}, "existing-id"),
        (
            Mock(spec=Request, state=Mock(request_id="request-id-from-state")),
            {"request_id": "existing-id", "other": "data"},
            "request-id-from-state",
        ),
    ]

response_success_flag_based_on_status_code_param_data = [
        (status.HTTP_200_OK, True), (status.HTTP_201_CREATED, True), (status.HTTP_204_NO_CONTENT, True),
        (status.HTTP_300_MULTIPLE_CHOICES, False), (status.HTTP_400_BAD_REQUEST, False), (status.HTTP_404_NOT_FOUND, False), (status.HTTP_500_INTERNAL_SERVER_ERROR, False),
    ]


# fmt: on
