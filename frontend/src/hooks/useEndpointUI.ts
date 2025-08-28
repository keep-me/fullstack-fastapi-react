import { useContext } from "react";
import { EndpointUIContext } from "../contexts/endpoint/EndpointUIContextDef";

export const useEndpointUI = () => {
  const context = useContext(EndpointUIContext);
  if (!context) {
    throw new Error("useEndpointUI must be used within an EndpointUIProvider");
  }
  return context;
};
