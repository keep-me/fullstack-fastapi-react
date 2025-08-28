import React from "react";
import { Box, Text, Input, Field } from "@chakra-ui/react";

interface UrlParametersFormProps {
  urlParams: Record<string, string>;
  urlParamErrors: Record<string, boolean>;
  endpoint: string;
  endpointId: string;
  onUrlParamChange: (
    paramName: string,
    value: string,
    endpointId: string,
    onUrlParamChange: (
      endpointId: string,
      paramName: string,
      value: string,
    ) => void,
  ) => void;
  onUrlParamChangeOriginal: (
    endpointId: string,
    paramName: string,
    value: string,
  ) => void;
}

const deepCompareRecord = (
  obj1: Record<string, string>,
  obj2: Record<string, string>,
): boolean => {
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (!(key in obj2)) return false;
    if (obj1[key] !== obj2[key]) return false;
  }

  return true;
};

const deepCompareBooleanRecord = (
  obj1: Record<string, boolean>,
  obj2: Record<string, boolean>,
): boolean => {
  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (const key of keys1) {
    if (!(key in obj2)) return false;
    if (obj1[key] !== obj2[key]) return false;
  }

  return true;
};

const areEqual = (
  prevProps: UrlParametersFormProps,
  nextProps: UrlParametersFormProps,
): boolean => {
  if (prevProps.endpoint !== nextProps.endpoint) return false;
  if (prevProps.endpointId !== nextProps.endpointId) return false;

  if (!deepCompareRecord(prevProps.urlParams, nextProps.urlParams))
    return false;

  if (
    !deepCompareBooleanRecord(
      prevProps.urlParamErrors,
      nextProps.urlParamErrors,
    )
  )
    return false;

  if (prevProps.onUrlParamChange !== nextProps.onUrlParamChange) return false;
  if (prevProps.onUrlParamChangeOriginal !== nextProps.onUrlParamChangeOriginal)
    return false;

  return true;
};

const UrlParametersForm: React.FC<UrlParametersFormProps> = ({
  urlParams,
  urlParamErrors,
  endpoint,
  endpointId,
  onUrlParamChange,
  onUrlParamChangeOriginal,
}) => {
  const hasUrlParams = Object.keys(urlParams).length > 0;

  if (!hasUrlParams) {
    return null;
  }

  return (
    <Box mb={4} id="url-params">
      <Text fontWeight="bold" mb={2}>
        URL Parameters
      </Text>
      {Object.entries(urlParams).map(([paramName, paramValue]) => {
        const pathParamNames =
          endpoint.match(/\{(\w+)\}/g)?.map((match) => match.slice(1, -1)) ||
          [];
        const isPathParam = pathParamNames.includes(paramName);

        return (
          <Field.Root
            key={paramName}
            mb={2}
            invalid={!!urlParamErrors[paramName]}
            required={isPathParam}
          >
            <Field.Label htmlFor={`${endpointId}-${paramName}`} fontSize="sm">
              {paramName} {isPathParam && <Field.RequiredIndicator />}
            </Field.Label>
            <Input
              id={`${endpointId}-${paramName}`}
              value={paramValue}
              onChange={(e) =>
                onUrlParamChange(
                  paramName,
                  e.target.value,
                  endpointId,
                  onUrlParamChangeOriginal,
                )
              }
              size="sm"
              type={
                paramName === "skip" || paramName === "limit"
                  ? "number"
                  : "text"
              }
              min={
                paramName === "skip" || paramName === "limit" ? 0 : undefined
              }
            />
            {urlParamErrors[paramName] && (
              <Field.ErrorText>This parameter is required</Field.ErrorText>
            )}
          </Field.Root>
        );
      })}
    </Box>
  );
};

export default React.memo(UrlParametersForm, areEqual);
