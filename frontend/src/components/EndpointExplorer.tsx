import { Box } from "@chakra-ui/react";
import { useGetUserMeQuery } from "@/redux/services/userApi";
import { ComposedEndpointProvider } from "@/contexts";
import EndpointList from "./EndpointList";

const EndpointExplorer: React.FC = () => {
  useGetUserMeQuery(undefined, {
    skip: true,
  });

  return (
    <ComposedEndpointProvider>
      <Box maxW="1200px" mx="auto" p={5}>
        <EndpointList />
      </Box>
    </ComposedEndpointProvider>
  );
};

export default EndpointExplorer;
