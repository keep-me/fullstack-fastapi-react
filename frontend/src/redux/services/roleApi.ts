import { api } from "./api";
import type {
  Role,
  RoleCreate,
  RoleUpdate,
  Permission,
  RoleWithUsers,
} from "@/types/role";

type ApiError = {
  status?: number;
  data?: {
    message?: string;
  };
  message?: string;
};

export const roleApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getRoles: builder.query<Role[], { skip?: number; limit?: number }>({
      query: ({ skip = 0, limit = 100 }) => ({
        url: `/api/v1/roles/?skip=${skip}&limit=${limit}`,
        method: "GET",
      }),
      transformResponse: (response: Role[]) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: ["RoleList"] as const,
    }),

    getRolesWithUserCount: builder.query<RoleWithUsers[], void>({
      query: () => ({
        url: "/api/v1/roles/with-users",
        method: "GET",
      }),
      transformResponse: (response: RoleWithUsers[]) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: ["RoleList"] as const,
    }),

    getRoleById: builder.query<Role, number>({
      query: (roleId) => ({
        url: `/api/v1/roles/${roleId}`,
        method: "GET",
      }),
      transformResponse: (response: Role) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: (_result, _error, roleId) => [
        { type: "Role" as const, id: roleId },
      ],
    }),

    createRole: builder.mutation<Role, RoleCreate>({
      query: (roleData) => ({
        url: "/api/v1/roles/",
        method: "POST",
        body: roleData,
      }),
      transformResponse: (response: Role) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: ["RoleList"] as const,
    }),

    updateRole: builder.mutation<Role, { roleId: number; roleData: RoleUpdate }>({
      query: ({ roleId, roleData }) => ({
        url: `/api/v1/roles/${roleId}`,
        method: "PATCH",
        body: roleData,
      }),
      transformResponse: (response: Role) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: (_result, _error, { roleId }) => [
        { type: "Role" as const, id: roleId },
        "RoleList",
      ],
    }),

    deleteRole: builder.mutation<void, number>({
      query: (roleId) => ({
        url: `/api/v1/roles/${roleId}`,
        method: "DELETE",
      }),
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: ["RoleList"] as const,
    }),

    assignPermissionsToRole: builder.mutation<Role, { roleId: number; permissionIds: number[] }>({
      query: ({ roleId, permissionIds }) => ({
        url: `/api/v1/roles/${roleId}/permissions`,
        method: "POST",
        body: permissionIds,
      }),
      transformResponse: (response: Role) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: (_result, _error, { roleId }) => [
        { type: "Role" as const, id: roleId },
        "RoleList",
      ],
    }),

    addPermissionToRole: builder.mutation<Role, { roleId: number; permissionId: number }>({
      query: ({ roleId, permissionId }) => ({
        url: `/api/v1/roles/${roleId}/permissions/${permissionId}`,
        method: "POST",
      }),
      transformResponse: (response: Role) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: (_result, _error, { roleId }) => [
        { type: "Role" as const, id: roleId },
        "RoleList",
      ],
    }),

    removePermissionFromRole: builder.mutation<Role, { roleId: number; permissionId: number }>({
      query: ({ roleId, permissionId }) => ({
        url: `/api/v1/roles/${roleId}/permissions/${permissionId}`,
        method: "DELETE",
      }),
      transformResponse: (response: Role) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: (_result, _error, { roleId }) => [
        { type: "Role" as const, id: roleId },
        "RoleList",
      ],
    }),

    getPermissions: builder.query<Permission[], { skip?: number; limit?: number }>({
      query: ({ skip = 0, limit = 100 }) => ({
        url: `/api/v1/permissions/?skip=${skip}&limit=${limit}`,
        method: "GET",
      }),
      transformResponse: (response: Permission[]) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: ["PermissionList"] as const,
    }),

    getPermissionsByResource: builder.query<Permission[], string>({
      query: (resource) => ({
        url: `/api/v1/permissions/by-resource/${resource}`,
        method: "GET",
      }),
      transformResponse: (response: Permission[]) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: ["PermissionList"] as const,
    }),

    getPermissionById: builder.query<Permission, number>({
      query: (permissionId) => ({
        url: `/api/v1/permissions/${permissionId}`,
        method: "GET",
      }),
      transformResponse: (response: Permission) => response,
      transformErrorResponse: (error: ApiError) => error,
      providesTags: (_result, _error, permissionId) => [
        { type: "Permission" as const, id: permissionId },
      ],
    }),

    createPermission: builder.mutation<Permission, Permission>({
      query: (permissionData) => ({
        url: "/api/v1/permissions/",
        method: "POST",
        body: permissionData,
      }),
      transformResponse: (response: Permission) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: ["PermissionList"] as const,
    }),

    updatePermission: builder.mutation<Permission, { permissionId: number; permissionData: Partial<Permission> }>({
      query: ({ permissionId, permissionData }) => ({
        url: `/api/v1/permissions/${permissionId}`,
        method: "PATCH",
        body: permissionData,
      }),
      transformResponse: (response: Permission) => response,
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: (_result, _error, { permissionId }) => [
        { type: "Permission" as const, id: permissionId },
        "PermissionList",
      ],
    }),

    deletePermission: builder.mutation<void, number>({
      query: (permissionId) => ({
        url: `/api/v1/permissions/${permissionId}`,
        method: "DELETE",
      }),
      transformErrorResponse: (error: ApiError) => error,
      invalidatesTags: ["PermissionList"] as const,
    }),
  }),
});

export const {
  useGetRolesQuery,
  useGetRolesWithUserCountQuery,
  useGetRoleByIdQuery,
  useCreateRoleMutation,
  useUpdateRoleMutation,
  useDeleteRoleMutation,
  useAssignPermissionsToRoleMutation,
  useAddPermissionToRoleMutation,
  useRemovePermissionFromRoleMutation,
  useGetPermissionsQuery,
  useGetPermissionsByResourceQuery,
  useGetPermissionByIdQuery,
  useCreatePermissionMutation,
  useUpdatePermissionMutation,
  useDeletePermissionMutation,
} = roleApi;
