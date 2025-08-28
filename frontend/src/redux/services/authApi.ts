import { api } from "./api";
import { getFingerprint } from "../utils/fingerprint";
import type { LoginCredentials, SignupCredentials } from "@/types/auth";

export const authApi = api.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation({
      async queryFn(
        credentials: LoginCredentials,
        _queryApi,
        _extraOptions,
        baseQuery,
      ) {
        const fingerprint = await getFingerprint();

        const body = {
          username: credentials.username || "",
          password: credentials.password || "",
          fingerprint,
        };

        const result = await baseQuery({
          url: "/api/v1/auth/login",
          method: "POST",
          body,
        });

        if (result.error) {
          return { error: result.error };
        }

        return { data: result.data };
      },
    }),
    refresh: builder.mutation({
      async queryFn(_: unknown, _queryApi, _extraOptions, baseQuery) {
        const fingerprint = await getFingerprint();

        const result = await baseQuery({
          url: "/api/v1/auth/refresh",
          method: "POST",
          body: { fingerprint },
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (result.error) {
          return { error: result.error };
        }

        return { data: result.data };
      },
    }),
    logout: builder.mutation({
      query: () => ({
        url: "/api/v1/auth/logout",
        method: "GET",
      }),
    }),
    signup: builder.mutation({
      async queryFn(
        credentials: SignupCredentials,
        _api,
        _extraOptions,
        baseQuery,
      ) {
        const body = {
          username: credentials.username || "",
          password: credentials.password || "",
          email: credentials.email || "",
          full_name: credentials.full_name || "",
        };

        const result = await baseQuery({
          url: "/api/v1/auth/signup",
          method: "POST",
          body,
        });

        if (result.error) {
          return { error: result.error };
        }

        return { data: result.data };
      },
    }),
    resetPassword: builder.mutation({
      async queryFn(email: string, _api, _extraOptions, baseQuery) {
        const result = await baseQuery({
          url: "/api/v1/auth/reset-password",
          method: "POST",
          body: { email },
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (result.error) {
          return { error: result.error };
        }

        return {
          data: {
            ...result.data,
            resetToken: result.resetToken,
          },
        };
      },
    }),
    verifyCode: builder.mutation({
      async queryFn(
        {
          code,
          verificationToken,
        }: { code: string; verificationToken: string },
        _api,
        _extraOptions,
        baseQuery,
      ) {
        const result = await baseQuery({
          url: "/api/v1/auth/verify-code",
          method: "POST",
          body: { code },
          headers: {
            "Content-Type": "application/json",
            "X-Verification": verificationToken,
          },
        });

        if (result.error) {
          return { error: result.error };
        }

        return {
          data: {
            ...result.data,
            resetToken: result.resetToken,
          },
        };
      },
    }),
    setNewPassword: builder.mutation({
      async queryFn(
        {
          new_password,
          confirm_new_password,
          verificationToken,
        }: {
          new_password: string;
          confirm_new_password: string;
          verificationToken: string;
        },
        _api,
        _extraOptions,
        baseQuery,
      ) {
        const result = await baseQuery({
          url: "/api/v1/auth/new-password",
          method: "POST",
          body: { new_password, confirm_new_password },
          headers: {
            "Content-Type": "application/json",
            "X-Verification": verificationToken,
          },
        });

        return result;
      },
    }),
  }),
});

export const {
  useLoginMutation,
  useRefreshMutation,
  useLogoutMutation,
  useSignupMutation,
  useResetPasswordMutation,
  useVerifyCodeMutation,
  useSetNewPasswordMutation,
} = authApi;
