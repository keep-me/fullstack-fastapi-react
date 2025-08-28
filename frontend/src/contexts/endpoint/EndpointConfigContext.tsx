import React, { useMemo, useState, useEffect } from "react";
import type { EndpointConfig } from "@/types/endpoints";
import { EndpointConfigContext } from "./EndpointConfigContextDef";

interface EndpointConfigProviderProps {
  children: React.ReactNode;
}

export const EndpointConfigProvider: React.FC<EndpointConfigProviderProps> = ({
  children,
}) => {
  const [endpointConfigs, setEndpointConfigs] = useState<
    Record<string, EndpointConfig>
  >({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadEndpointConfig = async () => {
      try {
        const { createEndpointConfig } = await import(
          "@/config/endpointConfig"
        );
        const configs = createEndpointConfig();
        setEndpointConfigs(configs);
      } catch (error) {
        console.error("Failed to load endpoint config:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadEndpointConfig();
  }, []);

  const value = useMemo(
    () => ({
      endpointConfigs,
      isLoading,
    }),
    [endpointConfigs, isLoading],
  );

  return (
    <EndpointConfigContext.Provider value={value}>
      {children}
    </EndpointConfigContext.Provider>
  );
};
