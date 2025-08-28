export const ENDPOINT_IDS = {
  HEALTH: "health",
  USERS_ME: "users-me",
  USERS_MY_ID: "users-my-id",
  USERS_LIST: "users-list",
  USERS_BY_ID: "users-by-id",
  USERS_UPDATE_BY_ID: "users-update-by-id",
  USERS_DELETE_BY_ID: "users-delete-by-id",
  USERS_CREATE: "users-create",
  USERS_DELETE_ME: "users-delete-me",
  USERS_UPDATE_ME: "users-update-me",
  USERS_UPDATE_PASSWORD: "users-update-password",
  AUTH_LOGIN: "auth-login",
  AUTH_SIGNUP: "auth-signup",
  AUTH_REFRESH: "auth-refresh",
  AUTH_LOGOUT: "auth-logout",
  AUTH_RESET_PASSWORD: "auth-reset-password",
  AUTH_VERIFY_CODE: "auth-verify-code",
  AUTH_NEW_PASSWORD: "auth-new-password",
} as const;

export type EndpointId = (typeof ENDPOINT_IDS)[keyof typeof ENDPOINT_IDS];

export const ENDPOINT_CATEGORIES = {
  AUTH: {
    title: "Auth",
    subtitle: "Authentication endpoints",
  },
  USERS: {
    title: "Users",
    subtitle: "User management endpoints",
  },
  OTHERS: {
    title: "Others",
    subtitle: "Other endpoints",
  },
} as const;
