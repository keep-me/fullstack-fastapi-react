import type { EndpointConfig } from "@/types/endpoints";
import { ENDPOINT_IDS, type EndpointId } from "@/constants/endpointConstants";
import { STORAGE_KEYS } from "@/config/env";

export const createEndpointConfig = (): Record<EndpointId, EndpointConfig> => {
  const getAuthToken = (): string => {
    const authData = localStorage.getItem(STORAGE_KEYS.AUTH)
      ? JSON.parse(localStorage.getItem(STORAGE_KEYS.AUTH)!)
      : null;
    return authData?.accessToken || "";
  };

  const getAuthHeaders = () => ({
    accept: "application/json",
    Authorization: `Bearer ${getAuthToken()}`,
  });

  const getJsonHeaders = () => ({
    accept: "application/json",
    "Content-Type": "application/json",
  });

  const getAuthJsonHeaders = () => ({
    ...getAuthHeaders(),
    "Content-Type": "application/json",
  });

  return {
    [ENDPOINT_IDS.AUTH_SIGNUP]: {
      method: "POST",
      path: "/api/v1/auth/signup",
      title: "Signup",
      subheader: "Register a new user in the system.",
      access: "PUBLIC",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        { name: "user_in", description: "User registration data" },
        { name: "bg_tasks", description: "Background tasks for sending email" },
        { name: "auth_service", description: "Auth service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description: "When username or email already exists.",
        },
      ],
      defaultBody: JSON.stringify(
        {
          username: "string",
          email: "string",
          full_name: "string",
          password: "string",
        },
        null,
        2,
      ),
      headers: getJsonHeaders,
    },
    [ENDPOINT_IDS.AUTH_LOGIN]: {
      method: "POST",
      path: "/api/v1/auth/login",
      title: "Login",
      subheader: "Login user to the system.",
      access: "PUBLIC",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        { name: "data", description: "User login data" },
        { name: "response", description: "FastAPI response object" },
        { name: "request", description: "FastAPI request object" },
        { name: "auth_service", description: "Auth service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description: "When credentials are invalid.",
        },
      ],
      returns: [{ name: "Token", description: "Access and refresh tokens." }],
      defaultBody: JSON.stringify(
        {
          username: "string",
          password: "string",
          fingerprint: "string",
        },
        null,
        2,
      ),
      headers: getJsonHeaders,
    },
    [ENDPOINT_IDS.AUTH_REFRESH]: {
      method: "POST",
      path: "/api/v1/auth/refresh",
      title: "Refresh",
      subheader: "Refresh user authentication tokens.",
      access: "AUTHORIZED",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        {
          name: "body",
          description: "Token refresh request data (contains fingerprint)",
        },
        { name: "request", description: "FastAPI request object" },
        { name: "response", description: "FastAPI response object" },
        { name: "auth_service", description: "Auth service dependency" },
      ],
      raises: [
        {
          name: "TokenError",
          description:
            "When tokens are invalid, missing, or session verification fails.",
        },
      ],
      returns: [
        {
          name: "Dict[str, Any]",
          description:
            "Standardized response with new access and refresh tokens.",
        },
      ],
      defaultBody: JSON.stringify(
        {
          fingerprint: "string",
        },
        null,
        2,
      ),
      headers: getAuthJsonHeaders,
    },
    [ENDPOINT_IDS.AUTH_LOGOUT]: {
      method: "GET",
      path: "/api/v1/auth/logout",
      title: "Logout",
      subheader: "Logout user from the system.",
      access: "AUTHORIZED",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        { name: "current_user", description: "Currently authenticated user" },
        { name: "request", description: "FastAPI request object" },
        { name: "response", description: "FastAPI response object" },
        { name: "auth_service", description: "Auth service dependency" },
      ],
      returns: [
        {
          name: "Dict[str, Any]",
          description: "Standardized response indicating successful logout.",
        },
      ],
      defaultBody: "Not required",
      headers: getAuthHeaders,
    },
    [ENDPOINT_IDS.AUTH_RESET_PASSWORD]: {
      method: "POST",
      path: "/api/v1/auth/reset-password",
      title: "Reset Password",
      subheader: "Initiates password reset process.",
      access: "PUBLIC",
      args: [
        { name: "request_data", description: "Request data with email" },
        {
          name: "request",
          description: "FastAPI request object (for rate limiting)",
        },
        {
          name: "response",
          description: "FastAPI response object (for rate limiting)",
        },
        { name: "auth_service", description: "Auth service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description: "If user is not found or inactive.",
        },
      ],
      returns: [
        {
          name: "JSONResponse",
          description:
            "Message about code sending with token in X-Verification header.",
        },
      ],
      defaultBody: JSON.stringify(
        {
          email: "admin@example.com",
        },
        null,
        2,
      ),
      headers: getJsonHeaders,
    },
    [ENDPOINT_IDS.AUTH_VERIFY_CODE]: {
      method: "POST",
      path: "/api/v1/auth/verify-code",
      title: "Verify Code",
      subheader: "Verifies confirmation code for password reset.",
      access: "PUBLIC",
      args: [
        { name: "code_data", description: "Confirmation code" },
        { name: "request", description: "FastAPI request object" },
        { name: "response", description: "FastAPI response object" },
        { name: "auth_service", description: "Auth service dependency" },
        { name: "email", description: "Email extracted from JWT token" },
      ],
      raises: [
        {
          name: "ValidationError",
          description: "If code is invalid or expired.",
        },
        {
          name: "TokenError",
          description: "If token is invalid or missing.",
        },
      ],
      returns: [
        {
          name: "JSONResponse",
          description:
            "Verification result with token in X-Verification header.",
        },
      ],
      defaultBody: JSON.stringify(
        {
          code: "123456",
        },
        null,
        2,
      ),
      headers: () => ({
        accept: "application/json",
        "Content-Type": "application/json",
        "X-Verification": "your-verification-token-here",
      }),
    },
    [ENDPOINT_IDS.AUTH_NEW_PASSWORD]: {
      method: "POST",
      path: "/api/v1/auth/new-password",
      title: "Set New Password",
      subheader: "Sets new user password.",
      access: "PUBLIC",
      args: [
        { name: "password_data", description: "New password and confirmation" },
        { name: "request", description: "FastAPI request object" },
        { name: "response", description: "FastAPI response object" },
        { name: "auth_service", description: "Auth service dependency" },
        { name: "email", description: "Email extracted from JWT token" },
      ],
      raises: [
        {
          name: "ValidationError",
          description: "If passwords don't match or session expired.",
        },
        {
          name: "UserAccessError",
          description: "If user is not found.",
        },
        {
          name: "TokenError",
          description: "If token is invalid or missing.",
        },
      ],
      returns: [
        {
          name: "JSONResponse",
          description: "Success message about password change.",
        },
      ],
      defaultBody: JSON.stringify(
        {
          new_password: "newpassword123",
          confirm_new_password: "newpassword123",
        },
        null,
        2,
      ),
      headers: () => ({
        accept: "application/json",
        "Content-Type": "application/json",
        "X-Verification": "your-verification-token-here",
      }),
    },
    [ENDPOINT_IDS.HEALTH]: {
      method: "GET",
      path: "/health",
      title: "Health Check",
      subheader: "Health check endpoint for monitoring.",
      access: "PUBLIC",
      returns: [{ name: "dict", description: "Status information." }],
      defaultBody: "Not required",
      headers: () => ({ accept: "application/json" }),
    },
    [ENDPOINT_IDS.USERS_ME]: {
      method: "GET",
      path: "/api/v1/users/me",
      title: "Get User Me",
      subheader: "Get current user information.",
      access: "AUTHORIZED",
      args: [
        { name: "current_user", description: "Currently authenticated user." },
      ],
      returns: [{ name: "UserPublic", description: "Current user data." }],
      defaultBody: "Not required",
      headers: getAuthHeaders,
    },
    [ENDPOINT_IDS.USERS_MY_ID]: {
      method: "GET",
      path: "/api/v1/users/my_id",
      title: "Get My Id",
      subheader: "Get current user ID.",
      access: "AUTHORIZED",
      args: [
        { name: "current_user", description: "Currently authenticated user." },
      ],
      returns: [{ name: "UUID", description: "Current user ID." }],
      defaultBody: "Not required",
      headers: getAuthHeaders,
    },
    [ENDPOINT_IDS.USERS_UPDATE_ME]: {
      method: "PATCH",
      path: "/api/v1/users/me",
      title: "Update User Me",
      subheader: "Update current user's information.",
      access: "AUTHORIZED",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        { name: "current_user", description: "Currently authenticated user" },
        { name: "user_in", description: "User update data" },
        { name: "user_service", description: "User service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description:
            "If a user with the same username or email already exists",
        },
        { name: "HTTPException", description: "If no update data provided" },
      ],
      returns: [{ name: "UserBase", description: "Updated user data." }],
      defaultBody: JSON.stringify(
        {
          username: "string",
          email: "string",
          full_name: "string",
        },
        null,
        2,
      ),
      headers: getAuthJsonHeaders,
    },
    [ENDPOINT_IDS.USERS_UPDATE_PASSWORD]: {
      method: "PATCH",
      path: "/api/v1/users/me/password",
      title: "Update Password Me",
      subheader: "Update current user's password.",
      access: "AUTHORIZED",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        { name: "current_user", description: "Currently authenticated user" },
        { name: "body", description: "Password update data" },
        { name: "user_service", description: "User service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description:
            "If current password is invalid or new password is same as current",
        },
        {
          name: "HTTPException",
          description: "If new password validation fails",
        },
      ],
      returns: [
        {
          name: "JSONResponse",
          description: "Success message with 200 status code.",
        },
      ],
      defaultBody: JSON.stringify(
        {
          current_password: "string",
          new_password: "string",
        },
        null,
        2,
      ),
      headers: getAuthJsonHeaders,
    },
    [ENDPOINT_IDS.USERS_DELETE_ME]: {
      method: "DELETE",
      path: "/api/v1/users/me",
      title: "Delete User Me",
      subheader: "Delete current user.",
      access: "AUTHORIZED",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        { name: "current_user", description: "Currently authenticated user" },
        { name: "user_service", description: "User service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description: "If attempting to delete admin account.",
        },
      ],
      returns: [
        {
          name: "JSONResponse",
          description: "Success message with 200 status code.",
        },
      ],
      defaultBody: "Not required",
      headers: getAuthHeaders,
    },
    [ENDPOINT_IDS.USERS_CREATE]: {
      method: "POST",
      path: "/api/v1/users/",
      title: "Create User",
      subheader: "Create a new user.",
      access: "ADMIN",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        {
          name: "current_superuser",
          description: "Currently authenticated superuser",
        },
        { name: "user_in", description: "User creation data" },
        { name: "user_service", description: "User service dependency" },
        { name: "bg_tasks", description: "Background tasks for sending email" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description:
            "If a user with the same username or email already exists.",
        },
      ],
      returns: [{ name: "UserPublic", description: "Created user data." }],
      defaultBody: JSON.stringify(
        {
          username: "string",
          email: "string",
          full_name: "string",
          password: "string",
          role: "USER",
          is_active: true,
        },
        null,
        2,
      ),
      headers: getAuthJsonHeaders,
    },
    [ENDPOINT_IDS.USERS_LIST]: {
      method: "GET",
      path: "/api/v1/users/",
      title: "Get Users List",
      subheader: "Get list of all users.",
      access: "ADMIN",
      args: [
        { name: "skip", description: "Number of users to skip." },
        { name: "limit", description: "Maximum number of users to return." },
        { name: "current_user", description: "Currently authenticated user." },
      ],
      returns: [{ name: "List[UserPublic]", description: "List of users." }],
      defaultBody: "Not required",
      headers: getAuthHeaders,
      urlParams: {
        skip: "0",
        limit: "10",
      },
    },
    [ENDPOINT_IDS.USERS_BY_ID]: {
      method: "GET",
      path: "/api/v1/users/{user_id}",
      title: "Get User By Id",
      subheader: "Get user by ID.",
      access: "ADMIN",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        {
          name: "current_superuser",
          description: "Current authenticated superuser",
        },
        { name: "user_id", description: "ID of the user to retrieve" },
        { name: "user_service", description: "User service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description: "If user with specified ID is not found.",
        },
      ],
      returns: [{ name: "UserPublic", description: "User data." }],
      defaultBody: "Not required",
      headers: getAuthHeaders,
      urlParams: {
        user_id: "",
      },
    },
    [ENDPOINT_IDS.USERS_UPDATE_BY_ID]: {
      method: "PATCH",
      path: "/api/v1/users/{user_id}",
      title: "Update User By Id",
      subheader: "Update user by ID.",
      access: "ADMIN",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        {
          name: "current_superuser",
          description: "Current authenticated superuser",
        },
        { name: "user_in", description: "User update data from admin" },
        { name: "user_id", description: "ID of the user to update" },
        { name: "user_service", description: "User service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description: "If user with specified ID is not found.",
        },
      ],
      returns: [{ name: "UserPublic", description: "Updated user data." }],
      defaultBody: JSON.stringify(
        {
          username: "string",
          password: "string",
          email: "string",
          full_name: "string",
          role: "ADMIN",
          is_active: true,
        },
        null,
        2,
      ),
      headers: getAuthJsonHeaders,
      urlParams: {
        user_id: "",
      },
    },
    [ENDPOINT_IDS.USERS_DELETE_BY_ID]: {
      method: "DELETE",
      path: "/api/v1/users/{user_id}",
      title: "Delete User By Id",
      subheader: "Delete user by ID.",
      access: "ADMIN",
      args: [
        { name: "uow", description: "Unit of Work dependency" },
        {
          name: "current_superuser",
          description: "Current authenticated superuser",
        },
        { name: "user_id", description: "ID of the user to delete" },
        { name: "user_service", description: "User service dependency" },
      ],
      raises: [
        {
          name: "UserAccessError",
          description:
            "If user with specified ID is not found or is an admin account.",
        },
      ],
      returns: [
        {
          name: "JSONResponse",
          description: "Success message with 200 status code.",
        },
      ],
      defaultBody: "Not required",
      headers: getAuthHeaders,
      urlParams: {
        user_id: "",
      },
    },
  };
};
