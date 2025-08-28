export interface LoginFormData {
  username: string;
  password: string;
}

export interface SignupFormData {
  username: string;
  email: string;
  full_name: string;
  password: string;
}

export interface UpdateUserFormData {
  username?: string;
  email?: string;
  full_name?: string;
}

export interface UpdatePasswordFormData {
  current_password: string;
  new_password: string;
}
