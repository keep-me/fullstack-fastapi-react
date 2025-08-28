import { api } from "./api";
import { getUserMe } from "../slices/user";
import type { User } from "@/types/user";
import type { UpdateUserFormData } from "@/types/forms";

type ApiError = {
  status?: number;
  data?: {
    message?: string;
  };
  message?: string;
};

export const userApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getUserMe: builder.query<User, void>({
      query: () => ({
        url: "/api/v1/users/me",
        method: "GET",
      }),
      transformResponse: (response: User) => {
        return response;
      },
      transformErrorResponse: (error: ApiError) => {
        return error;
      },
      providesTags: ["User"] as const,
      async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          if (data) {
            dispatch(getUserMe(data));
          }
        } catch {
          // Intentionally empty - error handling is done at component level
        }
      },
    }),
    updateUserMe: builder.mutation<User, UpdateUserFormData>({
      query: (userData) => ({
        url: "/api/v1/users/me",
        method: "PATCH",
        body: userData,
      }),
      transformResponse: (response: User) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: ["User"] as const,
      async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
        try {
          const { data } = await queryFulfilled;
          if (data) {
            dispatch(getUserMe(data));
          }
        } catch {
          // Intentionally empty - error handling is done at component level
        }
      },
    }),
    updatePassword: builder.mutation<
      void,
      {
        currentPassword: string;
        newPassword: string;
        confirmNewPassword: string;
      }
    >({
      query: ({ currentPassword, newPassword, confirmNewPassword }) => ({
        url: "/api/v1/users/me/password",
        method: "PATCH",
        body: {
          current_password: currentPassword,
          new_password: newPassword,
          confirm_new_password: confirmNewPassword,
        },
      }),
    }),
    deleteUserMe: builder.mutation<void, void>({
      query: () => ({
        url: "/api/v1/users/me",
        method: "DELETE",
      }),
    }),
    getAllUsers: builder.query<User[], { skip?: number; limit?: number }>({
      query: ({ skip = 0, limit = 10 }) => ({
        url: `/api/v1/users/?skip=${skip}&limit=${limit}`,
        method: "GET",
      }),
      transformResponse: (response: User[]) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: ["UserList"] as const,
    }),
    getUserById: builder.query<User, string>({
      query: (userId) => ({
        url: `/api/v1/users/${userId}`,
        method: "GET",
      }),
      transformResponse: (response: User) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: (_result, _error, userId) => [
        { type: "User" as const, id: userId },
      ],
    }),
    updateUserById: builder.mutation<
      User,
      { userId: string; userData: UpdateUserFormData }
    >({
      query: ({ userId, userData }) => ({
        url: `/api/v1/users/${userId}`,
        method: "PATCH",
        body: userData,
      }),
      transformResponse: (response: User) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: (_result, _error, { userId }) => [
        { type: "User" as const, id: userId },
        "UserList" as const,
      ],
    }),
    deleteUserById: builder.mutation<void, string>({
      query: (userId) => ({
        url: `/api/v1/users/${userId}`,
        method: "DELETE",
      }),
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: ["UserList"] as const,
    }),
    createUser: builder.mutation<User, Record<string, unknown>>({
      query: (userData) => ({
        url: "/api/v1/users/",
        method: "POST",
        body: userData,
      }),
      transformResponse: (response: User) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: ["UserList"] as const,
    }),
  }),
});

export const {
  useGetUserMeQuery,
  useUpdateUserMeMutation,
  useUpdatePasswordMutation,
  useDeleteUserMeMutation,
  useGetAllUsersQuery,
  useGetUserByIdQuery,
  useUpdateUserByIdMutation,
  useDeleteUserByIdMutation,
  useCreateUserMutation,
} = userApi;
