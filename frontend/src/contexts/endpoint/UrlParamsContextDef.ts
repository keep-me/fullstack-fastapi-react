import { createContext } from "react";
import type { EndpointConfig } from "@/types/endpoints";

interface UrlParamsContextType {
  urlParams: Record<string, Record<string, string>>;
  updateUrlParam: (
    endpointId: string,
    paramName: string,
    value: string,
  ) => void;
  resetUrlParams: (endpointId: string, config?: EndpointConfig) => void;
  getUrlParams: (endpointId: string) => Record<string, string>;
  isLoading: boolean;
}

export const UrlParamsContext = createContext<UrlParamsContextType | undefined>(
  undefined,
);
