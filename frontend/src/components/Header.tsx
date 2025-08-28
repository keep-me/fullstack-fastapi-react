import { useAppSelector } from "../redux/hooks";
import {
  Box,
  Flex,
  Heading,
  Spacer,
  Button,
  Portal,
  Dialog,
  CloseButton,
} from "@chakra-ui/react";
import { LuLockOpen, LuLock } from "react-icons/lu";
import { ColorModeButton } from "@/components/ui/color-mode";
import { useGetUserMeQuery } from "@/redux/services/userApi";
import AuthDialog from "./AuthDialog";
import { STORAGE_KEYS } from "@/config/env";

const Header: React.FC = () => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  const user = useAppSelector((state) => state.user);

  const { refetch: refetchUserData } = useGetUserMeQuery(undefined, {
    skip: !isAuthenticated,
  });

  const handleDialogOpen = () => {
    if (isAuthenticated) {
      refetchUserData();
    }
  };

  return (
    <Box borderBottomWidth="1px">
      <Flex align="center" p={{ base: 2, sm: 3 }} mx={2} gap={2} id="header">
        <Heading lineClamp={1} w={{ base: "240px", sm: "100%" }}>
          Fullstack FastAPI Template
        </Heading>
        <Spacer display={{ base: "block" }} />
        <ColorModeButton px={{ base: 2, sm: 3, md: 4 }} />
        <Dialog.Root placement="center">
          <Dialog.Trigger asChild>
            <Button
              id="auth-button"
              variant="subtle"
              size={{ base: "sm", md: "md" }}
              colorPalette={isAuthenticated ? "green" : "gray"}
              px={{ base: 2, sm: 3, md: 4 }}
              onClick={handleDialogOpen}
            >
              {isAuthenticated ? (
                <>
                  <LuLock />
                  <Box as="span" display={{ base: "none", sm: "inline" }}>
                    Authorized
                  </Box>
                </>
              ) : (
                <>
                  <LuLockOpen />
                  <Box as="span" display={{ base: "none", sm: "inline" }}>
                    Authorize
                  </Box>
                </>
              )}
            </Button>
          </Dialog.Trigger>
          <Portal>
            <Dialog.Backdrop style={{ backdropFilter: "blur(8px)" }} />
            <Dialog.Positioner>
              <Dialog.Content
                id="auth-form"
                maxW={{ base: "90vw", sm: "400px", md: "500px" }}
                w="100%"
              >
                <Dialog.Header>
                  <Dialog.Body>
                    <AuthDialog isAuthenticated={isAuthenticated} user={user} />
                  </Dialog.Body>
                  <Dialog.CloseTrigger asChild>
                    <CloseButton
                      position="absolute"
                      top={3}
                      right={3}
                      size="sm"
                      onClick={() => {
                        localStorage.removeItem(STORAGE_KEYS.RESET_TOKEN);
                      }}
                    />
                  </Dialog.CloseTrigger>
                </Dialog.Header>
              </Dialog.Content>
            </Dialog.Positioner>
          </Portal>
        </Dialog.Root>
      </Flex>
    </Box>
  );
};

export default Header;
