import { useState, useEffect } from "react";
import { useGetUserMeQuery } from "@/redux/services/userApi";
import { useAppSelector } from "@/redux/hooks";
import LoadingOverlay from "./LoadingOverlay";
import { Toaster } from "@/components/ui/toaster";
import type { AppInitializerProps } from "@/types/common";

/**
 * AppInitializer component that handles loading state and user authentication.
 * @param {Object} props - Component properties
 * @param {React.ReactNode} props.children - Child components to render
 * @returns {React.ReactElement} The AppInitializer component
 */
function AppInitializer({ children }: AppInitializerProps): React.ReactElement {
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const { accessToken, isAuthenticated } = useAppSelector(
    (state) => state.auth,
  );

  const hasToken: boolean = Boolean(accessToken && isAuthenticated);

  const { isLoading: isUserLoading } = useGetUserMeQuery(undefined, {
    skip: !hasToken,
    refetchOnMountOrArgChange: true,
  });

  useEffect((): void => {
    if (!hasToken) {
      setIsLoading(false);
      return;
    }

    if (!isUserLoading) {
      setIsLoading(false);
    }
  }, [isUserLoading, hasToken]);

  return (
    <>
      <LoadingOverlay isLoading={isLoading} />
      <Toaster />
      {children}
    </>
  );
}

export default AppInitializer;
