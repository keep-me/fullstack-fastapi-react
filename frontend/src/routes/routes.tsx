import { createBrowserRouter } from "react-router-dom";
import App from "../App";
import MainLayout from "@/layouts/MainLayout";
import PageNotFound404 from "@/components/PageNotFound404";
import RoleManagement from "@/components/RoleManagement";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <App />,
      },
      {
        path: "roles",
        element: <RoleManagement />,
      },
      {
        path: "*",
        element: <PageNotFound404 />,
      },
    ],
  },
]);

export default router;
