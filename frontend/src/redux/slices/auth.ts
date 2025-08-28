import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { STORAGE_KEYS } from "@/config/env";

const loadAuthState = () => {
  try {
    const authState = JSON.parse(
      localStorage.getItem(STORAGE_KEYS.AUTH) || "{}",
    );
    return authState;
  } catch {
    return {
      accessToken: null,
      isAuthenticated: false,
    };
  }
};

const initialState = loadAuthState();

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    login: (state, action: PayloadAction<{ access_token: string }>) => {
      state.accessToken = action.payload.access_token;
      state.isAuthenticated = true;

      localStorage.setItem(
        STORAGE_KEYS.AUTH,
        JSON.stringify({
          accessToken: state.accessToken,
          isAuthenticated: state.isAuthenticated,
        }),
      );
    },
    refresh: (state, action: PayloadAction<{ access_token: string }>) => {
      state.accessToken = action.payload.access_token;
      state.isAuthenticated = true;

      localStorage.setItem(
        STORAGE_KEYS.AUTH,
        JSON.stringify({
          accessToken: state.accessToken,
          isAuthenticated: state.isAuthenticated,
        }),
      );
    },
    logout: (state) => {
      localStorage.removeItem(STORAGE_KEYS.AUTH);
      state.accessToken = null;
      state.isAuthenticated = false;
    },
    clearAuth: (state) => {
      localStorage.removeItem(STORAGE_KEYS.AUTH);
      state.accessToken = null;
      state.isAuthenticated = false;
    },
    exampleLogin: () => {
      // Used for manual login from API explorer
    },
  },
});

export const { login, logout, clearAuth, refresh, exampleLogin } =
  authSlice.actions;
export default authSlice.reducer;
