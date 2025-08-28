import { createBrowserRouter } from "react-router-dom";
import App from "../App";
import MainLayout from "@/layouts/MainLayout";
import PageNotFound404 from "@/components/PageNotFound404";

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
        path: "*",
        element: <PageNotFound404 />,
      },
    ],
  },
]);

export default router;
