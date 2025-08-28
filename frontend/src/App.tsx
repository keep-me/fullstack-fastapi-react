import { Suspense, lazy } from "react";
import { Flex, Spinner, Text } from "@chakra-ui/react";

const EndpointExplorer = lazy(() => import("@/components/EndpointExplorer"));

const EndpointLoadingFallback = () => (
  <Flex direction="column" align="center" justify="center" minH="50vh" gap={4}>
    <Spinner size="xl" />
    <Text fontSize="lg" color="gray.500">
      Loading API Explorer...
    </Text>
  </Flex>
);

/**
 * Main application component that renders the EndpointExplorer component.
 * @returns {React.ReactElement} The App component
 */
function App(): React.ReactElement {
  return (
    <Suspense fallback={<EndpointLoadingFallback />}>
      <EndpointExplorer />
    </Suspense>
  );
}

export default App;
