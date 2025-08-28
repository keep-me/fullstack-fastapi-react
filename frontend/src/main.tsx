import { Provider as UIProvider } from "@/components/ui/provider";
import { Provider as ReduxProvider } from "react-redux";
import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import router from "./routes/routes";
import { store } from "./redux/store";
import { injectStore } from "./redux/services/api";
import AppInitializer from "./components/AppInitializer";

injectStore(store);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ReduxProvider store={store}>
      <UIProvider>
        <AppInitializer>
          <RouterProvider router={router} />
        </AppInitializer>
      </UIProvider>
    </ReduxProvider>
  </StrictMode>,
);
