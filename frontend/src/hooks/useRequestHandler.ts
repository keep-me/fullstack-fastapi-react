import { useCallback } from "react";
import { useAppDispatch } from "@/redux/hooks";
import { exampleLogin } from "@/redux/slices/auth";
import { axiosInstance } from "@/redux/services/api";
import { ENDPOINT_IDS } from "@/constants/endpointConstants";
import { API_BASE_URL } from "@/config/env";
import type { EndpointConfig } from "@/types/endpoints";
import type { ApiResponse } from "@/types/api";

interface UseRequestHandlerProps {
  endpointConfigs: Record<string, EndpointConfig>;
  requestBodies: Record<string, string>;
  urlParams: Record<string, Record<string, string>>;
  setLoadingState: (loading: boolean) => void;
  setEndpointResponse: (response: ApiResponse) => void;
  updateRequestDetails: (details: Record<string, unknown>) => void;
}

export const useRequestHandler = ({
  endpointConfigs,
  requestBodies,
  urlParams,
  setLoadingState,
  setEndpointResponse,
  updateRequestDetails,
}: UseRequestHandlerProps) => {
  const dispatch = useAppDispatch();

  const executeRequest = useCallback(
    async (endpointId: string) => {
      setLoadingState(true);

      try {
        const config = endpointConfigs[endpointId];
        if (!config) throw new Error("Endpoint configuration not found");

        let path = config.path;

        if (urlParams[endpointId]) {
          Object.entries(urlParams[endpointId]).forEach(
            ([paramName, paramValue]) => {
              path = path.replace(`{${paramName}}`, paramValue);
            },
          );
        }

        let url = `${API_BASE_URL}${path}`;
        if (urlParams[endpointId]) {
          const queryString = new URLSearchParams();
          const pathParamNames =
            config.path
              .match(/\{(\w+)\}/g)
              ?.map((match) => match.slice(1, -1)) || [];

          Object.entries(urlParams[endpointId]).forEach(
            ([paramName, paramValue]) => {
              if (
                !pathParamNames.includes(paramName) &&
                paramValue &&
                paramValue.trim() !== ""
              ) {
                queryString.append(paramName, paramValue);
              }
            },
          );

          if (queryString.toString()) {
            url += `?${queryString.toString()}`;
          }
        }

        const headers = config.headers();
        const axiosOptions: {
          method: string;
          url: string;
          headers: Record<string, string>;
          data?: unknown;
        } = {
          method: config.method,
          url: url,
          headers: headers,
        };

        if (
          config.method !== "GET" &&
          requestBodies[endpointId] !== "Not required"
        ) {
          axiosOptions.data = JSON.parse(requestBodies[endpointId]);
        }

        const axiosResponse = await axiosInstance(axiosOptions);

        const responseDetails: ApiResponse = {
          status: axiosResponse.status,
          statusText: axiosResponse.statusText,
          data: axiosResponse.data,
          headers: axiosResponse.headers as Record<string, string>,
        };

        setEndpointResponse(responseDetails);

        updateRequestDetails({
          url,
          method: config.method,
          headers,
          body: axiosOptions.data
            ? JSON.stringify(axiosOptions.data, null, 2)
            : null,
        });

        if (endpointId === ENDPOINT_IDS.AUTH_LOGIN) {
          dispatch(exampleLogin(axiosResponse.data));
        }
      } catch (error: unknown) {
        const axiosError = error as {
          message: string;
          response?: {
            status?: number;
            statusText?: string;
            data?: unknown;
            headers?: Record<string, string>;
          };
        };

        if (axiosError.response) {
          setEndpointResponse({
            status: axiosError.response.status || 500,
            statusText: axiosError.response.statusText || "Error",
            data: axiosError.response.data,
            headers: axiosError.response.headers || {},
          });
        } else {
          setEndpointResponse({
            status: 0,
            statusText: "Network Error",
            data: { message: axiosError.message },
            headers: {},
          });
        }
      } finally {
        setLoadingState(false);
      }
    },
    [
      endpointConfigs,
      requestBodies,
      urlParams,
      setLoadingState,
      setEndpointResponse,
      updateRequestDetails,
      dispatch,
    ],
  );

  return {
    executeRequest,
  };
};
