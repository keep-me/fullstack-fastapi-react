export interface Permission {
  id: number;
  name: string;
  description: string | null;
  resource: string;
  action: string;
}

export interface Role {
  id: number;
  name: "ADMIN" | "MANAGER" | "USER" | "GUEST";
  description: string | null;
  permissions: Permission[];
}

export interface RoleWithUsers extends Role {
  user_count: number;
}

export interface RoleCreate {
  name: "ADMIN" | "MANAGER" | "USER" | "GUEST";
  description?: string | null;
  permissions?: string[] | null;
}

export interface RoleUpdate {
  name?: "ADMIN" | "MANAGER" | "USER" | "GUEST" | null;
  description?: string | null;
  permissions?: string[] | null;
}

export interface PermissionCreate {
  name: string;
  description?: string | null;
  resource: string;
  action: string;
}

export interface PermissionUpdate {
  name?: string | null;
  description?: string | null;
  resource?: string | null;
  action?: string | null;
}

export interface AssignPermissionsRequest {
  role_id: number;
  permission_ids: number[];
}

export interface RoleState {
  roles: Role[];
  permissions: Permission[];
  selectedRole: Role | null;
  loading: boolean;
  error: string | null;
}
