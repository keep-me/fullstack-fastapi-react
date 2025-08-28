import React from "react";
import { Spinner, Flex, Text, Box } from "@chakra-ui/react";
import EndpointCategory from "./EndpointCategory";
import EndpointItem from "./EndpointItem";
import {
  useEndpointConfig,
  useEndpointUI,
  useEndpointData,
  useRequestBodies,
  useUrlParamsContext,
  useEndpointActions,
} from "@/hooks";

interface CategorySectionProps {
  title: string;
  subtitle: string;
  endpointIds: string[];
}

const arraysEqual = (arr1: string[], arr2: string[]): boolean => {
  if (arr1.length !== arr2.length) return false;
  return arr1.every((item, index) => item === arr2[index]);
};

const areEqual = (
  prevProps: CategorySectionProps,
  nextProps: CategorySectionProps,
): boolean => {
  if (prevProps.title !== nextProps.title) return false;
  if (prevProps.subtitle !== nextProps.subtitle) return false;

  if (!arraysEqual(prevProps.endpointIds, nextProps.endpointIds)) return false;

  return true;
};

const CategorySection: React.FC<CategorySectionProps> = ({
  title,
  subtitle,
  endpointIds,
}) => {
  const { endpointConfigs, isLoading: configLoading } = useEndpointConfig();
  const { expandedEndpoint } = useEndpointUI();
  const { isLoading, isTested, response, requestDetails } = useEndpointData();
  const { getRequestBody } = useRequestBodies();
  const { getUrlParams } = useUrlParamsContext();
  const {
    selectEndpoint,
    executeRequest,
    resetEndpoint,
    updateRequestBody,
    updateUrlParam,
  } = useEndpointActions();

  if (configLoading) {
    return (
      <EndpointCategory title={title} subtitle={subtitle}>
        <Box p={6}>
          <Flex align="center" justify="center" gap={3}>
            <Spinner size="sm" />
            <Text color="gray.500">Loading configuration...</Text>
          </Flex>
        </Box>
      </EndpointCategory>
    );
  }

  return (
    <EndpointCategory title={title} subtitle={subtitle}>
      {endpointIds.map((endpointId) => {
        const config = endpointConfigs[endpointId];
        if (!config) return null;

        return (
          <EndpointItem
            key={endpointId}
            method={config.method}
            endpoint={config.path}
            title={config.title}
            subheader={config.subheader}
            access={config.access}
            args={config.args || []}
            raises={config.raises || []}
            returns={config.returns || []}
            requestBody={getRequestBody(endpointId)}
            onBodyChange={(e) => updateRequestBody(endpointId, e.target.value)}
            endpointId={endpointId}
            expandedEndpoint={expandedEndpoint}
            onEndpointSelect={selectEndpoint}
            onTryEndpoint={() => executeRequest(endpointId)}
            onReset={resetEndpoint}
            isLoading={isLoading && expandedEndpoint === endpointId}
            isTested={isTested && expandedEndpoint === endpointId}
            response={response}
            requestDetails={requestDetails}
            urlParams={getUrlParams(endpointId)}
            onUrlParamChange={updateUrlParam}
          />
        );
      })}
    </EndpointCategory>
  );
};

export default React.memo(CategorySection, areEqual);
