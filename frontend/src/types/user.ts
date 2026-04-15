export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: "USER" | "ADMIN" | "MANAGER" | "GUEST";
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserState {
  id: string | null;
  username: string | null;
  email: string | null;
  full_name: string | null;
  role: "USER" | "ADMIN" | "MANAGER" | "GUEST" | null;
}
