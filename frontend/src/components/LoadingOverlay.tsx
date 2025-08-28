import { Box, Spinner } from "@chakra-ui/react";
import type { LoadingOverlayProps } from "@/types/components";

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ isLoading }) => {
  if (!isLoading) {
    return null;
  }

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      bg="rgba(0, 0, 0, 0.5)"
      display="flex"
      alignItems="center"
      justifyContent="center"
      zIndex={9999}
    >
      <Spinner size="xl" color="white" />
    </Box>
  );
};

export default LoadingOverlay;
