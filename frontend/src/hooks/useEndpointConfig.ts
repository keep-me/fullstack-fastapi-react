import { useContext } from "react";
import { EndpointConfigContext } from "../contexts/endpoint/EndpointConfigContextDef";

export const useEndpointConfig = () => {
  const context = useContext(EndpointConfigContext);
  if (!context) {
    throw new Error(
      "useEndpointConfig must be used within an EndpointConfigProvider",
    );
  }
  return context;
};
