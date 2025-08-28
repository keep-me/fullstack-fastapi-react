import { jwtDecode } from "jwt-decode";
import { getFingerprint } from "./fingerprint";
import { logout, refresh } from "../slices/auth";
import { clearUser } from "../slices/user";
import type { InternalAxiosRequestConfig, AxiosInstance } from "axios";
import type { AppDispatch } from "../store";
import type { JwtPayload } from "@/types/auth";
import { TOKEN_BUFFER_SECONDS, STORAGE_KEYS } from "@/config/env";

const _isTokenExpired = (token: string): boolean => {
  if (!token) return true;
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp <= currentTime + TOKEN_BUFFER_SECONDS;
  } catch {
    return true;
  }
};

export const performLogout = (dispatch: AppDispatch): void => {
  console.warn(
    "Performing automatic logout due to token authentication issues",
  );
  dispatch(logout());
  dispatch(clearUser());
  localStorage.removeItem(STORAGE_KEYS.AUTH);
  localStorage.removeItem(STORAGE_KEYS.USER);
};

export const refreshTokenMiddleware = async (
  config: InternalAxiosRequestConfig,
  dispatch: AppDispatch,
  refreshAxios: AxiosInstance,
): Promise<InternalAxiosRequestConfig> => {
  const publicEndpoints = [
    "/api/v1/auth/refresh",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/auth/signup",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/verify-code",
    "/api/v1/auth/new-password",
    "/health",
  ];

  const isPublicEndpoint =
    config.url &&
    publicEndpoints.some((endpoint) => {
      return config.url === endpoint || config.url!.endsWith(endpoint);
    });

  if (isPublicEndpoint) {
    return config;
  }

  const authState = JSON.parse(localStorage.getItem(STORAGE_KEYS.AUTH) || "{}");
  const accessToken = authState.accessToken;
  const isAuthenticated = authState.isAuthenticated;

  if (!accessToken || !isAuthenticated) {
    return config;
  }

  if (_isTokenExpired(accessToken)) {
    try {
      const fingerprint = await getFingerprint();

      const refreshResponse = await refreshAxios.post(
        `/api/v1/auth/refresh`,
        { fingerprint },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );

      if (refreshResponse.data.access_token) {
        const newAccessToken = refreshResponse.data.access_token;
        dispatch(refresh({ access_token: newAccessToken }));

        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${newAccessToken}`;
      } else {
        performLogout(dispatch);
        throw new Error("Refresh API returned empty token");
      }
    } catch (refreshError: unknown) {
      console.error("Refresh token failed:", refreshError);
      performLogout(dispatch);
      throw refreshError;
    }
  } else {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
};

export const createResponseInterceptor = () => {
  return async (error: unknown) => {
    return Promise.reject(error);
  };
};
