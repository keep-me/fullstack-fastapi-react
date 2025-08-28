import { useContext } from "react";
import { RequestBodiesContext } from "../contexts/endpoint/RequestBodiesContextDef";

export const useRequestBodies = () => {
  const context = useContext(RequestBodiesContext);
  if (!context) {
    throw new Error(
      "useRequestBodies must be used within a RequestBodiesProvider",
    );
  }
  return context;
};
