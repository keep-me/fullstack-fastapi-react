export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
export const TOAST_DURATION = Number(import.meta.env.VITE_TOAST_DURATION);
export const TOKEN_BUFFER_SECONDS = Number(
  import.meta.env.VITE_TOKEN_BUFFER_SECONDS,
);
export const RESEND_CODE_TIMER_SECONDS = Number(
  import.meta.env.VITE_RESEND_CODE_TIMER_SECONDS,
);
export const PASSWORD_RESET_REDIRECT_DELAY = Number(
  import.meta.env.VITE_PASSWORD_RESET_REDIRECT_DELAY,
);
export const FINGERPRINT_GENERATION_DELAY = Number(
  import.meta.env.VITE_FINGERPRINT_GENERATION_DELAY,
);
export const DEFAULT_FINGERPRINT_PREFIX = import.meta.env
  .VITE_DEFAULT_FINGERPRINT_PREFIX;

export const STORAGE_KEYS = {
  AUTH: import.meta.env.VITE_AUTH_STORAGE_KEY || "auth",
  USER: import.meta.env.VITE_USER_STORAGE_KEY || "user",
  FINGERPRINT: import.meta.env.VITE_FINGERPRINT_STORAGE_KEY || "fingerprint",
  RESET_TOKEN: import.meta.env.VITE_RESET_TOKEN_STORAGE_KEY || "reset-token",
} as const;
