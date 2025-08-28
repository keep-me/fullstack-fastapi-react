import { useContext } from "react";
import { EndpointDataContext } from "../contexts/endpoint/EndpointDataContextDef";

export const useEndpointData = () => {
  const context = useContext(EndpointDataContext);
  if (!context) {
    throw new Error(
      "useEndpointData must be used within an EndpointDataProvider",
    );
  }
  return context;
};
