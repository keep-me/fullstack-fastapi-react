import { createContext } from "react";

interface EndpointActionsContextType {
  selectEndpoint: (endpointId: string) => void;
  executeRequest: (endpointId: string) => void;
  resetEndpoint: () => void;
  updateRequestBody: (endpointId: string, body: string) => void;
  updateUrlParam: (
    endpointId: string,
    paramName: string,
    value: string,
  ) => void;
}

export const EndpointActionsContext = createContext<
  EndpointActionsContextType | undefined
>(undefined);
