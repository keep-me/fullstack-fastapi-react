import { Outlet } from "react-router-dom";
import Header from "@/components/Header";

type OutletContext = {
  user?: {
    id: string | null;
    username: string | null;
    email: string | null;
    full_name: string | null;
    role: string | null;
  };
};

const MainLayout: React.FC = () => {
  return (
    <>
      <Header />
      <main>
        <Outlet context={{} as OutletContext} />
      </main>
    </>
  );
};

export default MainLayout;
