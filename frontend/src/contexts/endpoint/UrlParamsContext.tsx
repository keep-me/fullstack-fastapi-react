import React from "react";
import { useUrlParams } from "@/hooks/useUrlParams";
import { useEndpointConfig } from "@/hooks/useEndpointConfig";
import { UrlParamsContext } from "./UrlParamsContextDef";

interface UrlParamsProviderProps {
  children: React.ReactNode;
}

export const UrlParamsProvider: React.FC<UrlParamsProviderProps> = ({
  children,
}) => {
  const { endpointConfigs, isLoading: configLoading } = useEndpointConfig();
  const urlParamsManager = useUrlParams(endpointConfigs);

  const getUrlParams = (endpointId: string): Record<string, string> => {
    return urlParamsManager.urlParams[endpointId] || {};
  };

  const value = {
    urlParams: urlParamsManager.urlParams,
    updateUrlParam: urlParamsManager.updateUrlParam,
    resetUrlParams: urlParamsManager.resetUrlParams,
    getUrlParams,
    isLoading: configLoading,
  };

  return (
    <UrlParamsContext.Provider value={value}>
      {children}
    </UrlParamsContext.Provider>
  );
};
