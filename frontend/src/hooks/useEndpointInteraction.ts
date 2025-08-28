import { useState, useCallback } from "react";
import type { RequestDetails } from "@/types/api";

export const useEndpointInteraction = () => {
  const [urlParamErrors, setUrlParamErrors] = useState<Record<string, boolean>>(
    {},
  );

  const getBadgeColor = useCallback((method: string): string => {
    switch (method.toUpperCase()) {
      case "GET":
        return "blue";
      case "POST":
        return "green";
      case "PUT":
        return "orange";
      case "PATCH":
        return "yellow";
      case "DELETE":
        return "red";
      default:
        return "gray";
    }
  }, []);

  const generateCurl = useCallback((requestDetails: RequestDetails): string => {
    const headers = Object.entries(requestDetails.headers)
      .filter(([, value]) => value)
      .map(([key, value]) => `-H "${key}: ${value}"`)
      .join(" \\\n  ");

    let curlCommand = `curl -X ${requestDetails.method} "${requestDetails.url}" \\\n  ${headers}`;

    if (requestDetails.method !== "GET" && requestDetails.body) {
      curlCommand += ` \\\n  -d '${requestDetails.body}'`;
    }

    return curlCommand;
  }, []);

  const validateUrlParams = useCallback(
    (urlParams: Record<string, string>, endpoint: string): boolean => {
      const errors: Record<string, boolean> = {};
      let hasErrors = false;

      const pathParamNames =
        endpoint.match(/\{(\w+)\}/g)?.map((match) => match.slice(1, -1)) || [];

      Object.entries(urlParams).forEach(([paramName, paramValue]) => {
        if (
          pathParamNames.includes(paramName) &&
          (!paramValue || paramValue.trim() === "")
        ) {
          errors[paramName] = true;
          hasErrors = true;
        }
      });

      setUrlParamErrors(errors);
      return !hasErrors;
    },
    [],
  );

  const handleTryEndpoint = useCallback(
    (
      urlParams: Record<string, string>,
      endpoint: string,
      onTryEndpoint: () => void,
    ) => {
      const hasUrlParams = Object.keys(urlParams).length > 0;

      if (hasUrlParams) {
        if (!validateUrlParams(urlParams, endpoint)) {
          return;
        }
      }

      setUrlParamErrors({});
      onTryEndpoint();
    },
    [validateUrlParams],
  );

  const handleUrlParamChange = useCallback(
    (
      paramName: string,
      value: string,
      endpointId: string,
      onUrlParamChange: (
        endpointId: string,
        paramName: string,
        value: string,
      ) => void,
    ) => {
      onUrlParamChange(endpointId, paramName, value);

      if (value && value.trim() !== "") {
        setUrlParamErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[paramName];
          return newErrors;
        });
      }
    },
    [],
  );

  const resetUrlParamErrors = useCallback(() => {
    setUrlParamErrors({});
  }, []);

  return {
    urlParamErrors,
    getBadgeColor,
    generateCurl,
    validateUrlParams,
    handleTryEndpoint,
    handleUrlParamChange,
    resetUrlParamErrors,
  };
};
