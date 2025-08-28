export interface AuthState {
  accessToken: string | null;
  isAuthenticated: boolean;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export type JwtPayload = {
  exp: number;
  sub: string;
};

export type LoginCredentials = {
  username?: string;
  password?: string;
};

export type SignupCredentials = {
  username?: string;
  password?: string;
  email?: string;
  full_name?: string;
};
