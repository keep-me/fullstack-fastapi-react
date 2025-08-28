import React from "react";
import { Box, Flex, Text, Button, VStack } from "@chakra-ui/react";

interface EndpointBodyProps {
  subheader: string;
  args: Array<{ name: string; description: string }>;
  raises: Array<{ name: string; description: string }>;
  returns: Array<{ name: string; description: string }>;
  isLoading: boolean;
  isTested: boolean;
  onTryEndpoint: () => void;
  onReset: () => void;
}

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

const areEqual = (
  prevProps: EndpointBodyProps,
  nextProps: EndpointBodyProps,
): boolean => {
  if (prevProps.subheader !== nextProps.subheader) return false;
  if (prevProps.isLoading !== nextProps.isLoading) return false;
  if (prevProps.isTested !== nextProps.isTested) return false;

  if (!arraysEqual(prevProps.args, nextProps.args)) return false;
  if (!arraysEqual(prevProps.raises, nextProps.raises)) return false;
  if (!arraysEqual(prevProps.returns, nextProps.returns)) return false;

  if (prevProps.onTryEndpoint !== nextProps.onTryEndpoint) return false;
  if (prevProps.onReset !== nextProps.onReset) return false;

  return true;
};

const EndpointBody: React.FC<EndpointBodyProps> = ({
  subheader,
  args = [],
  raises = [],
  returns = [],
  isTested,
  onTryEndpoint,
  onReset,
}) => {
  return (
    <Flex
      justifyContent="space-between"
      alignItems="flex-start"
      id={`endpoint-body`}
    >
      <Box mr={4}>
        <Text fontWeight="bold" mb={4}>
          {subheader}
        </Text>

        {args.length > 0 && (
          <Box mb={4}>
            <Text fontWeight="bold">Args:</Text>
            <Flex ml={4} flexDirection="column" gap={2}>
              {args.map((arg, index) => (
                <Flex
                  key={index}
                  flexDirection={{ base: "column", md: "row" }}
                  gap={{ base: 1, md: 2 }}
                >
                  <Text
                    color="purple.500"
                    fontWeight="semibold"
                    whiteSpace="nowrap"
                  >
                    {arg.name}
                  </Text>
                  <Text>{arg.description}</Text>
                </Flex>
              ))}
            </Flex>
          </Box>
        )}

        {raises.length > 0 && (
          <Box mb={4}>
            <Text fontWeight="bold">Raises:</Text>
            <Flex ml={4} flexDirection="column" gap={2}>
              {raises.map((raise, index) => (
                <Flex
                  key={index}
                  flexDirection={{ base: "column", md: "row" }}
                  gap={{ base: 1, md: 2 }}
                >
                  <Text color="red.500" fontWeight="semibold">
                    {raise.name}
                  </Text>
                  <Text>{raise.description}</Text>
                </Flex>
              ))}
            </Flex>
          </Box>
        )}

        {returns.length > 0 && (
          <Box mb={4}>
            <Text fontWeight="bold">Returns:</Text>
            <Flex ml={4} flexDirection="column" gap={2}>
              {returns.map((ret, index) => (
                <Flex
                  key={index}
                  flexDirection={{ base: "column", md: "row" }}
                  gap={{ base: 1, md: 2 }}
                >
                  <Text color="purple.500" fontWeight="semibold">
                    {ret.name}
                  </Text>
                  <Text>{ret.description}</Text>
                </Flex>
              ))}
            </Flex>
          </Box>
        )}
      </Box>

      <VStack>
        <Button
          onClick={onTryEndpoint}
          variant="surface"
          colorPalette="blue"
          size="sm"
          w="100px"
        >
          Try it out
        </Button>
        {isTested && (
          <Button
            onClick={onReset}
            colorPalette="red"
            variant="surface"
            size="sm"
            w="100px"
          >
            Reset
          </Button>
        )}
      </VStack>
    </Flex>
  );
};

export default React.memo(EndpointBody, areEqual);
