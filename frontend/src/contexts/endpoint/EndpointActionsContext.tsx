import React, { useCallback } from "react";
import { useRequestHandler } from "@/hooks/useRequestHandler";
import { useEndpointConfig } from "@/hooks/useEndpointConfig";
import { useEndpointUI } from "@/hooks/useEndpointUI";
import { useEndpointData } from "@/hooks/useEndpointData";
import { useRequestBodies } from "@/hooks/useRequestBodies";
import { useUrlParamsContext } from "@/hooks/useUrlParamsContext";
import { API_BASE_URL } from "@/config/env";
import type { EndpointConfig } from "@/types/endpoints";
import { EndpointActionsContext } from "./EndpointActionsContextDef";

interface EndpointActionsProviderProps {
  children: React.ReactNode;
}

export const EndpointActionsProvider: React.FC<
  EndpointActionsProviderProps
> = ({ children }) => {
  const { endpointConfigs } = useEndpointConfig();
  const { expandedEndpoint, setExpandedEndpoint } = useEndpointUI();
  const {
    setLoadingState,
    setEndpointResponse,
    updateRequestDetails,
    resetEndpointState,
  } = useEndpointData();
  const {
    requestBodies,
    updateRequestBody: updateRequestBodyInternal,
    resetRequestBody,
  } = useRequestBodies();
  const {
    urlParams,
    updateUrlParam: updateUrlParamInternal,
    resetUrlParams,
  } = useUrlParamsContext();

  const { executeRequest: executeRequestInternal } = useRequestHandler({
    endpointConfigs,
    requestBodies,
    urlParams,
    setLoadingState,
    setEndpointResponse,
    updateRequestDetails,
  });

  const selectEndpoint = useCallback(
    (endpointId: string) => {
      if (expandedEndpoint === endpointId) {
        setExpandedEndpoint(null);

        const config = endpointConfigs[endpointId] as EndpointConfig;
        if (config) {
          resetUrlParams(endpointId, config);
          resetRequestBody(endpointId);
        }
        return;
      }

      if (expandedEndpoint) {
        const prevConfig = endpointConfigs[expandedEndpoint] as EndpointConfig;
        if (prevConfig) {
          resetUrlParams(expandedEndpoint, prevConfig);
          resetRequestBody(expandedEndpoint);
        }
      }

      setExpandedEndpoint(endpointId);

      const config = endpointConfigs[endpointId] as EndpointConfig;
      if (config) {
        resetRequestBody(endpointId);

        resetEndpointState();

        let path = config.path;
        if (urlParams[endpointId]) {
          Object.entries(urlParams[endpointId]).forEach(
            ([paramName, paramValue]) => {
              path = path.replace(`{${paramName}}`, paramValue);
            },
          );
        }

        updateRequestDetails({
          url: `${API_BASE_URL}${path}`,
          method: config.method,
          headers: config.headers(),
          body:
            config.defaultBody !== "Not required" ? config.defaultBody : null,
        });
      }
    },
    [
      expandedEndpoint,
      setExpandedEndpoint,
      endpointConfigs,
      urlParams,
      resetUrlParams,
      resetRequestBody,
      resetEndpointState,
      updateRequestDetails,
    ],
  );

  const resetEndpoint = useCallback(() => {
    resetEndpointState();

    if (expandedEndpoint) {
      const config = endpointConfigs[expandedEndpoint] as EndpointConfig;
      if (config) {
        resetRequestBody(expandedEndpoint);

        resetUrlParams(expandedEndpoint, config);

        let path = config.path;
        if (config.urlParams) {
          Object.entries(config.urlParams).forEach(
            ([paramName, paramValue]) => {
              path = path.replace(`{${paramName}}`, paramValue);
            },
          );
        }

        updateRequestDetails({
          url: `${API_BASE_URL}${path}`,
          body:
            config.defaultBody !== "Not required" ? config.defaultBody : null,
        });
      }
    }
  }, [
    expandedEndpoint,
    endpointConfigs,
    resetEndpointState,
    resetRequestBody,
    resetUrlParams,
    updateRequestDetails,
  ]);

  const updateRequestBody = useCallback(
    (endpointId: string, body: string) => {
      updateRequestBodyInternal(endpointId, body);

      if (expandedEndpoint === endpointId) {
        updateRequestDetails({
          body: body !== "Not required" ? body : null,
        });
      }
    },
    [expandedEndpoint, updateRequestBodyInternal, updateRequestDetails],
  );

  const updateUrlParam = useCallback(
    (endpointId: string, paramName: string, value: string) => {
      updateUrlParamInternal(endpointId, paramName, value);

      if (expandedEndpoint === endpointId) {
        const config = endpointConfigs[endpointId] as EndpointConfig;
        if (!config) return;

        let path = config.path;
        const updatedParams = {
          ...urlParams[endpointId],
          [paramName]: value,
        };

        Object.entries(updatedParams).forEach(([pName, pValue]) => {
          path = path.replace(`{${pName}}`, pValue);
        });

        updateRequestDetails({
          url: `${API_BASE_URL}${path}`,
        });
      }
    },
    [
      expandedEndpoint,
      endpointConfigs,
      urlParams,
      updateUrlParamInternal,
      updateRequestDetails,
    ],
  );

  const value = {
    selectEndpoint,
    executeRequest: executeRequestInternal,
    resetEndpoint,
    updateRequestBody,
    updateUrlParam,
  };

  return (
    <EndpointActionsContext.Provider value={value}>
      {children}
    </EndpointActionsContext.Provider>
  );
};
