import { createContext } from "react";
import type { ApiResponse, RequestDetails } from "@/types/api";

interface EndpointDataContextType {
  response: ApiResponse | null;
  isLoading: boolean;
  isTested: boolean;
  requestDetails: RequestDetails;
  setResponse: (response: ApiResponse | null) => void;
  setLoadingState: (loading: boolean) => void;
  setEndpointResponse: (response: ApiResponse) => void;
  updateRequestDetails: (details: Partial<RequestDetails>) => void;
  resetEndpointState: () => void;
}

export const EndpointDataContext = createContext<
  EndpointDataContextType | undefined
>(undefined);
