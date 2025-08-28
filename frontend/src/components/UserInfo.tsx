import {
  Stack,
  Button,
  Input,
  Field,
  Skeleton,
  Clipboard,
  IconButton,
  InputGroup,
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import type { UserInfoProps } from "@/types/components";

const UserInfo: React.FC<UserInfoProps> = ({ user, onLogout }) => {
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(user.id === null);
  }, [user]);

  return (
    <Stack gap={{ base: 3, sm: 4, md: 5 }}>
      <Field.Root>
        <Field.Label>ID</Field.Label>
        <Skeleton
          loading={isLoading}
          width="full"
          height={{ base: "36px", md: "40px" }}
        >
          <Clipboard.Root value={user.id || ""}>
            <InputGroup
              endElement={
                <Clipboard.Trigger asChild>
                  <IconButton variant="surface" size="xs" me="-2">
                    <Clipboard.Indicator />
                  </IconButton>
                </Clipboard.Trigger>
              }
            >
              <Clipboard.Input asChild>
                <Input
                  value={user.id || ""}
                  disabled
                  bg="gray.200"
                  _dark={{ bg: "gray.800" }}
                />
              </Clipboard.Input>
            </InputGroup>
          </Clipboard.Root>
        </Skeleton>
      </Field.Root>
      <Field.Root>
        <Field.Label>Username</Field.Label>
        <Skeleton
          loading={isLoading}
          width="full"
          height={{ base: "36px", md: "40px" }}
        >
          <Input
            value={user.username || ""}
            disabled
            bg="gray.200"
            _dark={{ bg: "gray.800" }}
          />
        </Skeleton>
      </Field.Root>
      <Field.Root>
        <Field.Label>Full Name</Field.Label>
        <Skeleton
          loading={isLoading}
          width="full"
          height={{ base: "36px", md: "40px" }}
        >
          <Input
            value={user.full_name || ""}
            disabled
            bg="gray.200"
            _dark={{ bg: "gray.800" }}
          />
        </Skeleton>
      </Field.Root>
      <Field.Root>
        <Field.Label>Email</Field.Label>
        <Skeleton
          loading={isLoading}
          width="full"
          height={{ base: "36px", md: "40px" }}
        >
          <Input
            value={user.email || ""}
            disabled
            bg="gray.200"
            _dark={{ bg: "gray.800" }}
          />
        </Skeleton>
      </Field.Root>
      <Field.Root>
        <Field.Label>Role</Field.Label>
        <Skeleton
          loading={isLoading}
          width="full"
          height={{ base: "36px", md: "40px" }}
        >
          <Input
            value={user.role || ""}
            disabled
            bg="gray.200"
            _dark={{ bg: "gray.800" }}
          />
        </Skeleton>
      </Field.Root>
      <Button
        mt={4}
        colorPalette="red"
        onClick={onLogout}
        variant="surface"
        w={{ base: "120px", sm: "140px", md: "160px" }}
        size={{ base: "sm", md: "md" }}
        alignSelf="center"
      >
        Logout
      </Button>
    </Stack>
  );
};

export default UserInfo;
