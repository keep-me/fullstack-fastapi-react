import React from "react";
import {
  Box,
  HStack,
  Text,
  IconButton,
  Textarea,
  Separator,
  Clipboard,
} from "@chakra-ui/react";

interface RequestBodySectionProps {
  requestBody: string;
  onBodyChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

const areEqual = (
  prevProps: RequestBodySectionProps,
  nextProps: RequestBodySectionProps,
): boolean => {
  if (prevProps.requestBody !== nextProps.requestBody) return false;

  if (prevProps.onBodyChange !== nextProps.onBodyChange) return false;

  return true;
};

const RequestBodySection: React.FC<RequestBodySectionProps> = ({
  requestBody,
  onBodyChange,
}) => {
  if (requestBody === "Not required") {
    return null;
  }

  return (
    <>
      <Separator />
      <Box mt={4} id="request-body">
        <HStack>
          <Text fontWeight="bold">Request body</Text>
          <Clipboard.Root value={requestBody}>
            <Clipboard.Trigger asChild>
              <IconButton variant="surface" size="xs">
                <Clipboard.Indicator />
              </IconButton>
            </Clipboard.Trigger>
          </Clipboard.Root>
        </HStack>
        <Textarea
          value={requestBody}
          onChange={onBodyChange}
          mt={2}
          p={4}
          display="block"
          whiteSpace="pre"
          bg="gray.950"
          color="gray.100"
          fontFamily="monospace"
          fontSize="xs"
          autoresize
        />
      </Box>
    </>
  );
};

export default React.memo(RequestBodySection, areEqual);
