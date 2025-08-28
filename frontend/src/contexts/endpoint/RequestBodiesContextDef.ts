import { createContext } from "react";

interface RequestBodiesContextType {
  requestBodies: Record<string, string>;
  updateRequestBody: (endpointId: string, body: string) => void;
  resetRequestBody: (endpointId: string) => void;
  getRequestBody: (endpointId: string) => string;
}

export const RequestBodiesContext = createContext<
  RequestBodiesContextType | undefined
>(undefined);
