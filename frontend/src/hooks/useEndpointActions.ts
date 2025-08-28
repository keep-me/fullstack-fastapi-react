import { useContext } from "react";
import { EndpointActionsContext } from "../contexts/endpoint/EndpointActionsContextDef";

export const useEndpointActions = () => {
  const context = useContext(EndpointActionsContext);
  if (!context) {
    throw new Error(
      "useEndpointActions must be used within an EndpointActionsProvider",
    );
  }
  return context;
};
