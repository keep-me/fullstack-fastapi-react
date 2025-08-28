import { createContext } from "react";
import type { EndpointConfig } from "@/types/endpoints";

interface EndpointConfigContextType {
  endpointConfigs: Record<string, EndpointConfig>;
  isLoading: boolean;
}

export const EndpointConfigContext = createContext<
  EndpointConfigContextType | undefined
>(undefined);
