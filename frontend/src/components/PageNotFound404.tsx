import { Box, Heading, Text, Button } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";

const PageNotFound404 = () => {
  const navigate = useNavigate();

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="calc(100vh - 80px)"
      textAlign="center"
      px={4}
    >
      <Heading size="4xl" mb={4} color="gray.600">
        404
      </Heading>
      <Heading size="lg" mb={4}>
        Page Not Found
      </Heading>
      <Text fontSize="lg" color="gray.500" mb={8} maxWidth="xl">
        The page you are looking for doesn't exist or has been moved.
      </Text>
      <Button colorScheme="blue" size="lg" onClick={() => navigate("/")}>
        Go Home
      </Button>
    </Box>
  );
};

export default PageNotFound404;
