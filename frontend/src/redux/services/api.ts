import { createApi } from "@reduxjs/toolkit/query/react";
import axios from "axios";
import type { QueryArg } from "@/types/api";
import { API_BASE_URL } from "@/config/env";

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

const refreshAxios = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

import {
  refreshTokenMiddleware,
  createResponseInterceptor,
  performLogout,
} from "../utils/refreshTokenMiddleware";
import type { AppDispatch } from "../store";

let store: { dispatch: AppDispatch } | undefined;

const _isPublicEndpoint = (url?: string): boolean => {
  if (!url) return false;

  const publicEndpoints = [
    "/api/v1/auth/refresh",
    "/api/v1/auth/login",
    "/api/v1/auth/logout",
    "/api/v1/auth/signup",
    "/health",
  ];

  return publicEndpoints.some(
    (endpoint) => url === endpoint || url.endsWith(endpoint),
  );
};

axiosInstance.interceptors.request.use(
  async (config) => {
    try {
      if (store?.dispatch) {
        return await refreshTokenMiddleware(
          config,
          store.dispatch,
          refreshAxios,
        );
      }
      return config;
    } catch (error) {
      return Promise.reject(error);
    }
  },
  (error) => {
    return Promise.reject(error);
  },
);

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;
    const requestUrl = error.config?.url;

    if (status === 401 && !_isPublicEndpoint(requestUrl) && store?.dispatch) {
      console.warn(
        `Received ${status} error from ${requestUrl}, performing logout due to invalid token`,
      );
      performLogout(store.dispatch);
    } else if (status) {
      console.log(`Received ${status} error from ${requestUrl}`);
    }

    if (store?.dispatch) {
      const responseInterceptor = createResponseInterceptor();
      return responseInterceptor(error);
    }
    return Promise.reject(error);
  },
);

const axiosBaseQuery = () => {
  return async (queryArg: QueryArg) => {
    try {
      const { url, method = "GET", body, params, headers } = queryArg;

      if (!url) {
        throw new Error("URL not defined");
      }

      const config = {
        url,
        method,
        data: body,
        params,
        headers,
      };

      const result = await axiosInstance(config);

      return {
        data: result.data,
        resetToken:
          result.headers["x-verification"] || result.headers["X-Verification"],
      };
    } catch (axiosError: unknown) {
      const error = axiosError as {
        response?: { status?: number; data?: unknown };
        message?: string;
      };

      return {
        error: {
          status: error.response?.status,
          data: error.response?.data || error.message,
        },
      };
    }
  };
};

export const api = createApi({
  reducerPath: "api",
  baseQuery: axiosBaseQuery(),
  tagTypes: ["User", "UserList", "Role", "RoleList", "Permission", "PermissionList"],
  endpoints: () => ({}),
  refetchOnReconnect: true,
  refetchOnMountOrArgChange: 30,
});

const injectStore = (_store: { dispatch: AppDispatch }) => {
  store = _store;
};

export { axiosInstance, injectStore };
