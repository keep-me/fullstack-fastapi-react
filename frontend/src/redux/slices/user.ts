import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { UserState, User } from "@/types/user";
import { STORAGE_KEYS } from "@/config/env";

const loadUserState = () => {
  try {
    const userState = JSON.parse(
      localStorage.getItem(STORAGE_KEYS.USER) || "{}",
    );
    return userState;
  } catch {
    return {
      id: null,
      username: null,
      email: null,
      full_name: null,
      role: null,
    };
  }
};

const initialState: UserState = loadUserState();

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    getUserMe: (state, action: PayloadAction<User>) => {
      if (!action.payload) return;

      state.id = action.payload.id || null;
      state.username = action.payload.username || null;
      state.email = action.payload.email || null;
      state.full_name = action.payload.full_name || null;
      state.role = action.payload.role || null;

      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(state));
    },
    clearUser: (state) => {
      localStorage.removeItem(STORAGE_KEYS.USER);

      state.id = null;
      state.username = null;
      state.email = null;
      state.full_name = null;
      state.role = null;
    },
  },
});

export const { clearUser, getUserMe } = userSlice.actions;
export default userSlice.reducer;
