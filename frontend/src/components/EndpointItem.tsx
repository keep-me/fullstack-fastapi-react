import React, { useEffect, Suspense, lazy } from "react";
import { Box, Collapsible, Spinner, Flex } from "@chakra-ui/react";
import { useAppSelector } from "@/redux/hooks";
import { useEndpointInteraction } from "@/hooks/useEndpointInteraction";
import EndpointHeader from "./EndpointHeader";
import EndpointBody from "./EndpointBody";
import UrlParametersForm from "./UrlParametersForm";
import RequestBodySection from "./RequestBodySection";
import type { EndpointItemProps } from "@/types/components";

const ResponseTabs = lazy(() => import("./ResponseTabs"));

const ResponseTabsLoadingFallback = () => (
  <Flex justify="center" align="center" py={4}>
    <Spinner size="md" />
  </Flex>
);

const arraysEqual = (
  arr1: Array<{ name: string; description: string }>,
  arr2: Array<{ name: string; description: string }>,
): boolean => {
  if (arr1.length !== arr2.length) return false;
  return arr1.every((item1, index) => {
    const item2 = arr2[index];
    return item1.name === item2.name && item1.description === item2.description;
  });
};

const deepEqual = (
  obj1: Record<string, unknown>,
  obj2: Record<string, unknown>,
): boolean => {
  if (obj1 === obj2) return true;

  if (obj1 == null || obj2 == null) return obj1 === obj2;

  if (typeof obj1 !== typeof obj2) return false;

  if (typeof obj1 !== "object") return obj1 === obj2;

  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (!keys2.includes(key)) return false;
    if (
      !deepEqual(
        obj1[key] as Record<string, unknown>,
        obj2[key] as Record<string, unknown>,
      )
    )
      return false;
  }

  return true;
};

const areEqual = (
  prevProps: EndpointItemProps,
  nextProps: EndpointItemProps,
): boolean => {
  if (prevProps.method !== nextProps.method) return false;
  if (prevProps.endpoint !== nextProps.endpoint) return false;
  if (prevProps.title !== nextProps.title) return false;
  if (prevProps.subheader !== nextProps.subheader) return false;
  if (prevProps.access !== nextProps.access) return false;
  if (prevProps.requestBody !== nextProps.requestBody) return false;
  if (prevProps.endpointId !== nextProps.endpointId) return false;
  if (prevProps.expandedEndpoint !== nextProps.expandedEndpoint) return false;
  if (prevProps.isLoading !== nextProps.isLoading) return false;
  if (prevProps.isTested !== nextProps.isTested) return false;

  if (!arraysEqual(prevProps.args, nextProps.args)) return false;
  if (!arraysEqual(prevProps.raises, nextProps.raises)) return false;
  if (!arraysEqual(prevProps.returns, nextProps.returns)) return false;

  if (!deepEqual(prevProps.urlParams, nextProps.urlParams)) return false;

  if (!deepEqual(prevProps.response || {}, nextProps.response || {}))
    return false;
  if (
    !deepEqual(prevProps.requestDetails || {}, nextProps.requestDetails || {})
  )
    return false;

  if (prevProps.onBodyChange !== nextProps.onBodyChange) return false;
  if (prevProps.onEndpointSelect !== nextProps.onEndpointSelect) return false;
  if (prevProps.onTryEndpoint !== nextProps.onTryEndpoint) return false;
  if (prevProps.onReset !== nextProps.onReset) return false;
  if (prevProps.onUrlParamChange !== nextProps.onUrlParamChange) return false;

  return true;
};

/**
 * Component for displaying API endpoint.
 * @param {Object} props - Component properties
 * @param {string} props.method - HTTP method (GET, POST, PUT, PATCH, DELETE)
 * @param {string} props.endpoint - Endpoint URL
 * @param {string} props.title - Endpoint title
 * @param {string} props.subheader - Endpoint subheader/description
 * @param {Array} props.args - Endpoint arguments (array of objects {name, description})
 * @param {Array} props.raises - Endpoint exceptions (array of objects {name, description})
 * @param {Array} props.returns - Return values (array of objects {name, description})
 * @param {string} props.requestBody - Request body
 * @param {Function} props.onBodyChange - Request body change handler
 * @param {string} props.endpointId - Unique endpoint identifier
 * @param {string} props.expandedEndpoint - Currently expanded endpoint
 * @param {Function} props.onEndpointSelect - Endpoint selection handler
 * @param {Function} props.onTryEndpoint - "Try it out" button click handler
 * @param {Function} props.onReset - "Reset" button click handler
 * @param {boolean} props.isLoading - Loading flag
 * @param {boolean} props.isTested - Testing flag
 * @param {Object} props.response - Server response
 * @param {Object} props.requestDetails - Request details
 * @param {Object} props.urlParams - Endpoint URL parameters
 * @param {Function} props.onUrlParamChange - URL parameter change handler
 */
function EndpointItem({
  method,
  endpoint,
  title,
  subheader,
  access,
  args = [],
  raises = [],
  returns = [],
  requestBody,
  onBodyChange,
  endpointId,
  expandedEndpoint,
  onEndpointSelect,
  onTryEndpoint,
  onReset,
  isLoading,
  isTested,
  response,
  requestDetails,
  urlParams = {},
  onUrlParamChange,
}: EndpointItemProps): React.ReactElement {
  const {
    urlParamErrors,
    getBadgeColor,
    generateCurl,
    handleTryEndpoint,
    handleUrlParamChange,
    resetUrlParamErrors,
  } = useEndpointInteraction();

  const isAuthenticated: boolean = useAppSelector(
    (state) => state.auth.isAuthenticated,
  );
  const user = useAppSelector((state) => state.user);
  const isAdmin: boolean = user.role === "ADMIN";

  const isExpanded: boolean = expandedEndpoint === endpointId;

  const handleTryClick = (): void => {
    handleTryEndpoint(urlParams, endpoint, onTryEndpoint);
  };

  useEffect(() => {
    if (!isExpanded) {
      resetUrlParamErrors();
    }
  }, [isExpanded, resetUrlParamErrors]);

  return (
    <Collapsible.Root open={isExpanded} unmountOnExit>
      <Box
        border="1px solid"
        borderColor="bg.emphasized"
        bg="bg.muted"
        borderRadius="md"
        mb={4}
        id={`endpoint-item-${endpointId}`}
      >
        <Collapsible.Trigger asChild>
          <EndpointHeader
            method={method}
            endpoint={endpoint}
            title={title}
            access={access}
            isAuthenticated={isAuthenticated}
            isAdmin={isAdmin}
            isExpanded={isExpanded}
            endpointId={endpointId}
            onEndpointSelect={onEndpointSelect}
            getBadgeColor={getBadgeColor}
          />
        </Collapsible.Trigger>

        <Collapsible.Content>
          <Box p={4} borderTop="1px solid" borderColor="bg.emphasized">
            <EndpointBody
              subheader={subheader}
              args={args}
              raises={raises}
              returns={returns}
              isLoading={isLoading}
              isTested={isTested}
              onTryEndpoint={handleTryClick}
              onReset={onReset}
            />

            <UrlParametersForm
              urlParams={urlParams}
              urlParamErrors={urlParamErrors}
              endpoint={endpoint}
              endpointId={endpointId}
              onUrlParamChange={handleUrlParamChange}
              onUrlParamChangeOriginal={onUrlParamChange}
            />

            <RequestBodySection
              requestBody={requestBody}
              onBodyChange={onBodyChange}
            />

            {isTested && isExpanded && (
              <Suspense fallback={<ResponseTabsLoadingFallback />}>
                <ResponseTabs
                  response={response}
                  isLoading={isLoading}
                  requestDetails={requestDetails}
                  generateCurl={generateCurl}
                />
              </Suspense>
            )}
          </Box>
        </Collapsible.Content>
      </Box>
    </Collapsible.Root>
  );
}

export default React.memo(EndpointItem, areEqual);
