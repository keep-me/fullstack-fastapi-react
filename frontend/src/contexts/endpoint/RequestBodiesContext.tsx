import React, { useState, useCallback, useEffect } from "react";
import { useEndpointConfig } from "@/hooks/useEndpointConfig";
import { RequestBodiesContext } from "./RequestBodiesContextDef";
import type { EndpointConfig } from "@/types/endpoints";

interface RequestBodiesProviderProps {
  children: React.ReactNode;
}

export const RequestBodiesProvider: React.FC<RequestBodiesProviderProps> = ({
  children,
}) => {
  const { endpointConfigs } = useEndpointConfig();

  const [requestBodies, setRequestBodies] = useState<Record<string, string>>(
    {},
  );

  useEffect(() => {
    const bodies: Record<string, string> = {};
    Object.entries(endpointConfigs).forEach(([id, config]) => {
      bodies[id] = (config as EndpointConfig).defaultBody;
    });

    setRequestBodies((prevBodies) => {
      const hasChanges =
        Object.keys(bodies).length !== Object.keys(prevBodies).length ||
        Object.keys(bodies).some((id) => prevBodies[id] !== bodies[id]);

      return hasChanges ? bodies : prevBodies;
    });
  }, [endpointConfigs]);

  const updateRequestBody = useCallback((endpointId: string, body: string) => {
    setRequestBodies((prev) => ({
      ...prev,
      [endpointId]: body,
    }));
  }, []);

  const resetRequestBody = useCallback(
    (endpointId: string) => {
      const config = endpointConfigs[endpointId] as EndpointConfig;
      if (config) {
        setRequestBodies((prev) => ({
          ...prev,
          [endpointId]: config.defaultBody,
        }));
      }
    },
    [endpointConfigs],
  );

  const getRequestBody = useCallback(
    (endpointId: string): string => {
      return requestBodies[endpointId] || "";
    },
    [requestBodies],
  );

  const value = {
    requestBodies,
    updateRequestBody,
    resetRequestBody,
    getRequestBody,
  };

  return (
    <RequestBodiesContext.Provider value={value}>
      {children}
    </RequestBodiesContext.Provider>
  );
};
