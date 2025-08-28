import React from "react";
import { EndpointConfigProvider } from "./EndpointConfigContext";
import { EndpointUIProvider } from "./EndpointUIContext";
import { EndpointDataProvider } from "./EndpointDataContext";
import { RequestBodiesProvider } from "./RequestBodiesContext";
import { UrlParamsProvider } from "./UrlParamsContext";
import { EndpointActionsProvider } from "./EndpointActionsContext";

interface ComposedEndpointProviderProps {
  children: React.ReactNode;
}

export const ComposedEndpointProvider: React.FC<
  ComposedEndpointProviderProps
> = ({ children }) => {
  return (
    <EndpointConfigProvider>
      <EndpointUIProvider>
        <EndpointDataProvider>
          <RequestBodiesProvider>
            <UrlParamsProvider>
              <EndpointActionsProvider>{children}</EndpointActionsProvider>
            </UrlParamsProvider>
          </RequestBodiesProvider>
        </EndpointDataProvider>
      </EndpointUIProvider>
    </EndpointConfigProvider>
  );
};
