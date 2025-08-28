import { useContext } from "react";
import { UrlParamsContext } from "../contexts/endpoint/UrlParamsContextDef";

export const useUrlParamsContext = () => {
  const context = useContext(UrlParamsContext);
  if (!context) {
    throw new Error(
      "useUrlParamsContext must be used within a UrlParamsProvider",
    );
  }
  return context;
};
