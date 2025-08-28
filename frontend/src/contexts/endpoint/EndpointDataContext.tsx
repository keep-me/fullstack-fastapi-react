import React, { useState, useCallback, useEffect } from "react";
import { STORAGE_KEYS, API_BASE_URL } from "@/config/env";
import type { ApiResponse, RequestDetails } from "@/types/api";
import { EndpointDataContext } from "./EndpointDataContextDef";

interface EndpointDataProviderProps {
  children: React.ReactNode;
}

export const EndpointDataProvider: React.FC<EndpointDataProviderProps> = ({
  children,
}) => {
  const [response, setResponseState] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoadingState] = useState(false);
  const [isTested, setIsTestedState] = useState(false);
  const [requestDetails, setRequestDetailsState] = useState<RequestDetails>({
    url: `${API_BASE_URL}/api/v1/users/me`,
    method: "GET",
    headers: {
      accept: "application/json",
      Authorization: "",
    },
    body: null,
  });

  useEffect(() => {
    const authData = localStorage.getItem(STORAGE_KEYS.AUTH)
      ? JSON.parse(localStorage.getItem(STORAGE_KEYS.AUTH)!)
      : null;
    if (authData && authData.accessToken) {
      setRequestDetailsState((prev) => ({
        ...prev,
        headers: {
          ...prev.headers,
          Authorization: `Bearer ${authData.accessToken}`,
        },
      }));
    }
  }, []);

  const setResponse = useCallback((newResponse: ApiResponse | null) => {
    setResponseState(newResponse);
  }, []);

  const setLoadingState = useCallback((loading: boolean) => {
    setIsLoadingState(loading);
    if (loading) {
      setIsTestedState(true);
    }
  }, []);

  const setEndpointResponse = useCallback((newResponse: ApiResponse) => {
    setResponseState(newResponse);
    setIsTestedState(true);
  }, []);

  const updateRequestDetails = useCallback(
    (details: Partial<RequestDetails>) => {
      setRequestDetailsState((prev) => ({ ...prev, ...details }));
    },
    [],
  );

  const resetEndpointState = useCallback(() => {
    setResponseState(null);
    setIsTestedState(false);
  }, []);

  const value = {
    response,
    isLoading,
    isTested,
    requestDetails,
    setResponse,
    setLoadingState,
    setEndpointResponse,
    updateRequestDetails,
    resetEndpointState,
  };

  return (
    <EndpointDataContext.Provider value={value}>
      {children}
    </EndpointDataContext.Provider>
  );
};
