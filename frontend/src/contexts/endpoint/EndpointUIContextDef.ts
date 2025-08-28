import { createContext } from "react";

interface EndpointUIContextType {
  expandedEndpoint: string | null;
  setExpandedEndpoint: (endpointId: string | null) => void;
}

export const EndpointUIContext = createContext<
  EndpointUIContextType | undefined
>(undefined);
