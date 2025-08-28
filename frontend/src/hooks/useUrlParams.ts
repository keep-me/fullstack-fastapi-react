import { useState, useCallback, useEffect } from "react";
import type { EndpointConfig } from "@/types/endpoints";

export const useUrlParams = (
  endpointConfigs: Record<string, EndpointConfig>,
) => {
  const [urlParams, setUrlParams] = useState<
    Record<string, Record<string, string>>
  >({});

  useEffect(() => {
    const params: Record<string, Record<string, string>> = {};
    Object.entries(endpointConfigs).forEach(([id, config]) => {
      if (config.urlParams) {
        params[id] = { ...config.urlParams };
      }
    });

    setUrlParams((prevParams) => {
      const hasChanges =
        Object.keys(params).length !== Object.keys(prevParams).length ||
        Object.keys(params).some(
          (id) =>
            !prevParams[id] ||
            JSON.stringify(params[id]) !== JSON.stringify(prevParams[id]),
        );

      return hasChanges ? params : prevParams;
    });
  }, [endpointConfigs]);

  const updateUrlParam = useCallback(
    (endpointId: string, paramName: string, value: string) => {
      setUrlParams((prev) => ({
        ...prev,
        [endpointId]: {
          ...prev[endpointId],
          [paramName]: value,
        },
      }));
    },
    [],
  );

  const resetUrlParams = useCallback(
    (endpointId: string, config?: EndpointConfig) => {
      if (config && config.urlParams) {
        setUrlParams((prev) => ({
          ...prev,
          [endpointId]: { ...config.urlParams },
        }));
      }
    },
    [],
  );

  const getUrlParamsForEndpoint = useCallback(
    (endpointId: string) => {
      return urlParams[endpointId] || {};
    },
    [urlParams],
  );

  return {
    urlParams,
    updateUrlParam,
    resetUrlParams,
    getUrlParamsForEndpoint,
  };
};
