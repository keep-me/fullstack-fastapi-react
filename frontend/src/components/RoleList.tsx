import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Text,
  Badge,
  Spinner,
  Dialog,
  IconButton,
  Tooltip,
  Portal,
} from "@chakra-ui/react";
import { useState } from "react";
import { LuLock, LuEye, LuChevronUp } from "react-icons/lu";
import {
  useGetRolesQuery,
  useDeleteRoleMutation,
} from "@/redux/services/roleApi";
import type { Role } from "@/types/role";
import { toaster } from "@/components/ui/toaster";
import { TOAST_DURATION } from "@/config/env";

interface RoleListProps {
  onSelectRole: (role: Role) => void;
  selectedRoleId: number | null;
}

const RoleList: React.FC<RoleListProps> = ({ onSelectRole, selectedRoleId }) => {
  const { data: roles, isLoading, error, refetch } = useGetRolesQuery({ skip: 0, limit: 100 });
  const [deleteRole] = useDeleteRoleMutation();
  const [deleteConfirmRole, setDeleteConfirmRole] = useState<Role | null>(null);

  const handleDeleteRole = async (role: Role) => {
    try {
      await deleteRole(role.id).unwrap();
      toaster.create({
        title: "Role deleted",
        description: `Role ${role.name} has been deleted successfully`,
        type: "success",
        duration: TOAST_DURATION,
      });
      refetch();
    } catch (err: unknown) {
      const errorMessage =
        (err as { data?: { message?: string } })?.data?.message ||
        "Failed to delete role";
      toaster.create({
        title: "Error",
        description: errorMessage,
        type: "error",
        duration: TOAST_DURATION,
      });
    } finally {
      setDeleteConfirmRole(null);
    }
  };

  const getRoleColor = (roleName: string) => {
    switch (roleName) {
      case "ADMIN":
        return "red";
      case "MANAGER":
        return "orange";
      case "USER":
        return "blue";
      case "GUEST":
        return "gray";
      default:
        return "gray";
    }
  };

  if (isLoading) {
    return (
      <Flex justify="center" align="center" py={8}>
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Box p={4} textAlign="center">
        <Text color="red.500">Failed to load roles</Text>
        <Button mt={2} onClick={() => refetch()}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Flex align="center" mb={4} gap={2}>
        <LuLock size={24} />
        <Heading size="md">Roles</Heading>
      </Flex>

      <Box display="flex" flexDirection="column" gap={3}>
        {roles?.map((role) => (
          <Card.Root
            key={role.id}
            variant="outline"
            cursor="pointer"
            bg={selectedRoleId === role.id ? "blue.50" : undefined}
            _dark={{ bg: selectedRoleId === role.id ? "blue.900" : undefined }}
            onClick={() => onSelectRole(role)}
          >
            <Card.Body p={4}>
              <Flex justify="space-between" align="center">
                <Flex align="center" gap={3}>
                  <Badge colorPalette={getRoleColor(role.name)} size="lg">
                    {role.name}
                  </Badge>
                  <Text fontSize="sm" color="gray.500">
                    {role.description || "No description"}
                  </Text>
                </Flex>
                <Flex gap={2}>
                  <Tooltip content="Edit role">
                    <IconButton
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectRole(role);
                      }}
                    >
                      <LuEye />
                    </IconButton>
                  </Tooltip>
                  {role.name !== "ADMIN" && (
                    <Tooltip content="Delete role">
                      <IconButton
                        variant="ghost"
                        size="sm"
                        colorPalette="red"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteConfirmRole(role);
                        }}
                      >
                        <LuLock />
                      </IconButton>
                    </Tooltip>
                  )}
                </Flex>
              </Flex>
              <Flex mt={2} gap={2} flexWrap="wrap">
                <Text fontSize="xs" color="gray.500">
                  Permissions:
                </Text>
                {role.permissions.slice(0, 5).map((perm) => (
                  <Badge key={perm.id} size="sm" variant="subtle">
                    {perm.name}
                  </Badge>
                ))}
                {role.permissions.length > 5 && (
                  <Badge size="sm" variant="subtle">
                    +{role.permissions.length - 5} more
                  </Badge>
                )}
              </Flex>
            </Card.Body>
          </Card.Root>
        ))}
      </Box>

      <Dialog.Root
        open={!!deleteConfirmRole}
        onOpenChange={() => setDeleteConfirmRole(null)}
      >
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content>
              <Dialog.Header>Delete Role</Dialog.Header>
              <Dialog.Body>
                <Text>
                  Are you sure you want to delete the role{" "}
                  <strong>{deleteConfirmRole?.name}</strong>?
                </Text>
                <Text mt={2} fontSize="sm" color="gray.500">
                  This action cannot be undone.
                </Text>
              </Dialog.Body>
              <Dialog.Footer>
                <Dialog.CloseTrigger asChild>
                  <Button variant="surface">Cancel</Button>
                </Dialog.CloseTrigger>
                <Button
                  colorPalette="red"
                  onClick={() => deleteConfirmRole && handleDeleteRole(deleteConfirmRole)}
                >
                  Delete
                </Button>
              </Dialog.Footer>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>
    </Box>
  );
};

export default RoleList;
