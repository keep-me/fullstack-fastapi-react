import React, { useState, useCallback } from "react";
import { EndpointUIContext } from "./EndpointUIContextDef";

interface EndpointUIProviderProps {
  children: React.ReactNode;
}

export const EndpointUIProvider: React.FC<EndpointUIProviderProps> = ({
  children,
}) => {
  const [expandedEndpoint, setExpandedEndpointState] = useState<string | null>(
    null,
  );

  const setExpandedEndpoint = useCallback((endpointId: string | null) => {
    setExpandedEndpointState(endpointId);
  }, []);

  const value = {
    expandedEndpoint,
    setExpandedEndpoint,
  };

  return (
    <EndpointUIContext.Provider value={value}>
      {children}
    </EndpointUIContext.Provider>
  );
};
