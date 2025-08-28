import { useState, useCallback } from "react";
import type { ApiResponse, RequestDetails } from "@/types/api";
import { API_BASE_URL } from "@/config/env";

export const useEndpointManager = () => {
  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTested, setIsTested] = useState(false);
  const [requestDetails, setRequestDetails] = useState<RequestDetails>({
    url: `${API_BASE_URL}/api/v1/users/me`,
    method: "GET",
    headers: {
      accept: "application/json",
      Authorization: "",
    },
    body: null,
  });

  const updateRequestDetails = useCallback(
    (details: Partial<RequestDetails>) => {
      setRequestDetails((prev) => ({ ...prev, ...details }));
    },
    [],
  );

  const resetEndpointState = useCallback(() => {
    setResponse(null);
    setIsTested(false);
  }, []);

  const setEndpointResponse = useCallback((newResponse: ApiResponse) => {
    setResponse(newResponse);
    setIsTested(true);
  }, []);

  const setLoadingState = useCallback((loading: boolean) => {
    setIsLoading(loading);
    if (loading) {
      setIsTested(true);
    }
  }, []);

  return {
    expandedEndpoint,
    response,
    isLoading,
    isTested,
    requestDetails,

    setExpandedEndpoint,
    updateRequestDetails,
    resetEndpointState,
    setEndpointResponse,
    setLoadingState,
  };
};
