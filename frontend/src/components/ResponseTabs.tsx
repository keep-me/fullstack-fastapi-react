import React from "react";
import {
  Box,
  Flex,
  Text,
  Badge,
  IconButton,
  HStack,
  Spinner,
  Code,
  Tabs,
  Clipboard,
} from "@chakra-ui/react";
import type { ApiResponse, RequestDetails } from "@/types/api";

interface ResponseTabsProps {
  response: ApiResponse | null;
  isLoading: boolean;
  requestDetails: RequestDetails;
  generateCurl: (requestDetails: RequestDetails) => string;
}

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
  prevProps: ResponseTabsProps,
  nextProps: ResponseTabsProps,
): boolean => {
  if (prevProps.isLoading !== nextProps.isLoading) return false;

  if (!deepEqual(prevProps.response || {}, nextProps.response || {}))
    return false;

  if (
    !deepEqual(prevProps.requestDetails || {}, nextProps.requestDetails || {})
  )
    return false;

  try {
    const prevCurl = prevProps.generateCurl(prevProps.requestDetails);
    const nextCurl = nextProps.generateCurl(nextProps.requestDetails);
    if (prevCurl !== nextCurl) return false;
  } catch {
    return false;
  }

  return true;
};

const ResponseTabs: React.FC<ResponseTabsProps> = ({
  response,
  isLoading,
  requestDetails,
  generateCurl,
}) => {
  return (
    <Box mt={4} id={"endpoint-response"}>
      <Tabs.Root defaultValue="response">
        <Tabs.List>
          <Tabs.Trigger value="response" id="response-tab">
            Response
          </Tabs.Trigger>
          <Tabs.Trigger value="curl" id="curl-tab">
            cURL
          </Tabs.Trigger>
          <Tabs.Trigger value="url" id="request-url-tab">
            Request URL
          </Tabs.Trigger>
          <Tabs.Trigger value="headers" id="headers-tab">
            Headers
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="response">
          <Box mt={4}>
            <Flex justify="space-between" align="center" mb={2}>
              <HStack>
                <Text fontWeight="bold" id="response-title">
                  Response
                </Text>
                <Clipboard.Root value={JSON.stringify(response?.data, null, 2)}>
                  <Clipboard.Trigger asChild>
                    <IconButton variant="surface" size="xs">
                      <Clipboard.Indicator />
                    </IconButton>
                  </Clipboard.Trigger>
                </Clipboard.Root>
              </HStack>
              {response && !isLoading && (
                <Badge
                  id={"response-status-code"}
                  colorPalette={
                    response.status >= 200 && response.status < 300
                      ? "green"
                      : "red"
                  }
                >
                  {response.status} {response.statusText}
                </Badge>
              )}
            </Flex>
            {isLoading ? (
              <Spinner size="md" />
            ) : (
              <Code
                display="block"
                p={4}
                whiteSpace="pre"
                bg="gray.950"
                color="gray.100"
                maxH="500px"
                overflowY="auto"
                id="response-code"
              >
                {response
                  ? JSON.stringify(response.data, null, 2)
                  : "Not available"}
              </Code>
            )}
          </Box>
        </Tabs.Content>

        <Tabs.Content value="curl">
          <Box mt={4}>
            <Flex justify="space-between" align="center" mb={2}>
              <HStack>
                <Text fontWeight="bold" id="curl-title">
                  cURL
                </Text>
                <Clipboard.Root value={generateCurl(requestDetails)}>
                  <Clipboard.Trigger asChild>
                    <IconButton variant="surface" size="xs">
                      <Clipboard.Indicator />
                    </IconButton>
                  </Clipboard.Trigger>
                </Clipboard.Root>
              </HStack>
            </Flex>
            {isLoading ? (
              <Spinner size="md" />
            ) : (
              <Code
                display="block"
                p={4}
                whiteSpace="pre"
                bg="gray.950"
                color="gray.100"
                overflowX="auto"
                id="curl-code"
              >
                {generateCurl(requestDetails)}
              </Code>
            )}
          </Box>
        </Tabs.Content>

        <Tabs.Content value="url">
          <Box mt={4}>
            <Flex justify="space-between" align="center" mb={2}>
              <HStack>
                <Text fontWeight="bold" id="request-url-title">
                  Request URL
                </Text>
                <Clipboard.Root value={requestDetails.url}>
                  <Clipboard.Trigger asChild>
                    <IconButton variant="surface" size="xs">
                      <Clipboard.Indicator />
                    </IconButton>
                  </Clipboard.Trigger>
                </Clipboard.Root>
              </HStack>
            </Flex>
            {isLoading ? (
              <Spinner size="md" />
            ) : (
              <Code
                display="block"
                p={4}
                whiteSpace="pre"
                bg="gray.950"
                color="gray.100"
                id="request-url-code"
              >
                {requestDetails.url}
              </Code>
            )}
          </Box>
        </Tabs.Content>

        <Tabs.Content value="headers">
          <Box mt={4}>
            <Flex justify="space-between" align="center" mb={2}>
              <HStack>
                <Text fontWeight="bold" id="request-headers-title">
                  Request Headers
                </Text>
                <Clipboard.Root
                  value={JSON.stringify(requestDetails.headers, null, 2)}
                >
                  <Clipboard.Trigger asChild>
                    <IconButton variant="surface" size="xs">
                      <Clipboard.Indicator />
                    </IconButton>
                  </Clipboard.Trigger>
                </Clipboard.Root>
              </HStack>
            </Flex>
            {isLoading ? (
              <Spinner size="md" />
            ) : (
              <Code
                display="block"
                p={4}
                whiteSpace="pre"
                bg="gray.950"
                color="gray.100"
                overflowX="auto"
                id="request-headers-code"
              >
                {JSON.stringify(requestDetails.headers, null, 2)}
              </Code>
            )}
            {response && response.headers && (
              <>
                <HStack>
                  <Text
                    fontWeight="bold"
                    mt={4}
                    mb={2}
                    id="response-headers-title"
                  >
                    Response Headers
                  </Text>
                  <Clipboard.Root
                    value={JSON.stringify(response.headers, null, 2)}
                  >
                    <Clipboard.Trigger asChild>
                      <IconButton variant="surface" size="xs">
                        <Clipboard.Indicator />
                      </IconButton>
                    </Clipboard.Trigger>
                  </Clipboard.Root>
                </HStack>
                {isLoading ? (
                  <Spinner size="md" />
                ) : (
                  <Code
                    display="block"
                    p={4}
                    whiteSpace="pre"
                    bg="gray.950"
                    color="gray.100"
                    overflowX="auto"
                    id="response-headers-code"
                  >
                    {JSON.stringify(response.headers, null, 2)}
                  </Code>
                )}
              </>
            )}
          </Box>
        </Tabs.Content>
      </Tabs.Root>
    </Box>
  );
};

export default React.memo(ResponseTabs, areEqual);
