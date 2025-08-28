import { configureStore } from "@reduxjs/toolkit";
import { api, injectStore } from "./services/api";
import authReducer from "./slices/auth";
import userReducer from "./slices/user";

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    auth: authReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(api.middleware),
});

injectStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
