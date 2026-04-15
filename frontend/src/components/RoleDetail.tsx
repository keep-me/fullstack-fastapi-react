import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Text,
  Input,
  Textarea,
  Field,
  Select,
  Checkbox,
  Spinner,
  Badge,
  Divider,
  IconButton,
  Tooltip,
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { LuPlus, LuX, LuSave, LuShield } from "react-icons/lu";
import {
  useGetRoleByIdQuery,
  useUpdateRoleMutation,
  useGetPermissionsQuery,
  useCreateRoleMutation,
} from "@/redux/services/roleApi";
import type { Role, RoleUpdate, RoleCreate } from "@/types/role";
import { toaster } from "@/components/ui/toaster";
import { TOAST_DURATION } from "@/config/env";

interface RoleDetailProps {
  roleId: number | null;
  onClose: () => void;
  onSaved: () => void;
}

const RoleDetail: React.FC<RoleDetailProps> = ({ roleId, onClose, onSaved }) => {
  const isNewRole = roleId === null;
  const { data: role, isLoading: roleLoading } = useGetRoleByIdQuery(roleId!, {
    skip: isNewRole,
  });
  const { data: permissions, isLoading: permissionsLoading } = useGetPermissionsQuery({
    skip: 0,
    limit: 100,
  });
  const [updateRole] = useUpdateRoleMutation();
  const [createRole] = useCreateRoleMutation();

  const [formData, setFormData] = useState<{
    name: RoleCreate["name"];
    description: string;
    selectedPermissions: number[];
  }>({
    name: "USER",
    description: "",
    selectedPermissions: [],
  });

  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (role) {
      setFormData({
        name: role.name,
        description: role.description || "",
        selectedPermissions: role.permissions.map((p) => p.id),
      });
    }
  }, [role]);

  const handlePermissionToggle = (permissionId: number) => {
    setFormData((prev) => ({
      ...prev,
      selectedPermissions: prev.selectedPermissions.includes(permissionId)
        ? prev.selectedPermissions.filter((id) => id !== permissionId)
        : [...prev.selectedPermissions, permissionId],
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const permissionNames = permissions
        ?.filter((p) => formData.selectedPermissions.includes(p.id))
        .map((p) => p.name);

      if (isNewRole) {
        const roleCreate: RoleCreate = {
          name: formData.name,
          description: formData.description || null,
          permissions: permissionNames,
        };
        await createRole(roleCreate).unwrap();
        toaster.create({
          title: "Role created",
          description: "Role has been created successfully",
          type: "success",
          duration: TOAST_DURATION,
        });
      } else {
        const roleUpdate: RoleUpdate = {
          name: formData.name,
          description: formData.description || null,
          permissions: permissionNames,
        };
        await updateRole({
          roleId: roleId!,
          roleData: roleUpdate,
        }).unwrap();
        toaster.create({
          title: "Role updated",
          description: "Role has been updated successfully",
          type: "success",
          duration: TOAST_DURATION,
        });
      }
      onSaved();
    } catch (err: unknown) {
      const errorMessage =
        (err as { data?: { message?: string } })?.data?.message ||
        "Failed to save role";
      toaster.create({
        title: "Error",
        description: errorMessage,
        type: "error",
        duration: TOAST_DURATION,
      });
    } finally {
      setIsSaving(false);
    }
  };

  const getPermissionsByResource = () => {
    if (!permissions) return {};
    return permissions.reduce((acc, perm) => {
      if (!acc[perm.resource]) {
        acc[perm.resource] = [];
      }
      acc[perm.resource].push(perm);
      return acc;
    }, {} as Record<string, typeof permissions>);
  };

  if (roleLoading && !isNewRole) {
    return (
      <Flex justify="center" align="center" py={8}>
        <Spinner size="xl" />
      </Flex>
    );
  }

  const permissionsByResource = getPermissionsByResource();

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Flex align="center" gap={2}>
          <LuShield size={24} />
          <Heading size="md">
            {isNewRole ? "Create New Role" : `Edit Role: ${role?.name}`}
          </Heading>
        </Flex>
        <Tooltip content="Close">
          <IconButton variant="ghost" onClick={onClose}>
            <LuX />
          </IconButton>
        </Tooltip>
      </Flex>

      <Card.Root variant="outline" mb={6}>
        <Card.Header>
          <Heading size="sm">Role Information</Heading>
        </Card.Header>
        <Card.Body>
          <Flex direction="column" gap={4}>
            <Field.Root>
              <Field.Label>Role Name</Field.Label>
              <Select.Root
                value={formData.name}
                onValueChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    name: e.value as RoleCreate["name"],
                  }))
                }
                disabled={!isNewRole}
              >
                <Select.Trigger>
                  <Select.ValueText placeholder="Select role" />
                </Select.Trigger>
                <Select.Content>
                  <Select.Item value="ADMIN">ADMIN</Select.Item>
                  <Select.Item value="MANAGER">MANAGER</Select.Item>
                  <Select.Item value="USER">USER</Select.Item>
                  <Select.Item value="GUEST">GUEST</Select.Item>
                </Select.Content>
              </Select.Root>
            </Field.Root>

            <Field.Root>
              <Field.Label>Description</Field.Label>
              <Textarea
                value={formData.description}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, description: e.target.value }))
                }
                placeholder="Enter role description"
                rows={3}
              />
            </Field.Root>
          </Flex>
        </Card.Body>
      </Card.Root>

      <Card.Root variant="outline" mb={6}>
        <Card.Header>
          <Flex justify="space-between" align="center">
            <Heading size="sm">Permissions</Heading>
            <Badge size="sm">
              {formData.selectedPermissions.length} selected
            </Badge>
          </Flex>
        </Card.Header>
        <Card.Body>
          {permissionsLoading ? (
            <Flex justify="center" py={4}>
              <Spinner />
            </Flex>
          ) : (
            <Flex direction="column" gap={6}>
              {Object.entries(permissionsByResource).map(([resource, perms]) => (
                <Box key={resource}>
                  <Flex align="center" gap={2} mb={3}>
                    <Badge colorPalette="blue" size="md">
                      {resource}
                    </Badge>
                    <Text fontSize="sm" color="gray.500">
                      ({perms.filter((p) => formData.selectedPermissions.includes(p.id)).length}/{perms.length})
                    </Text>
                  </Flex>
                  <Flex flexWrap="wrap" gap={3}>
                    {perms.map((perm) => (
                      <Checkbox.Root
                        key={perm.id}
                        checked={formData.selectedPermissions.includes(perm.id)}
                        onCheckedChange={() => handlePermissionToggle(perm.id)}
                      >
                        <Checkbox.HiddenInput />
                        <Checkbox.Control />
                        <Checkbox.Label>
                          <Flex align="center" gap={2}>
                            <Text fontSize="sm" fontWeight="medium">
                              {perm.action}
                            </Text>
                            {perm.description && (
                              <Text fontSize="xs" color="gray.500">
                                ({perm.description})
                              </Text>
                            )}
                          </Flex>
                        </Checkbox.Label>
                      </Checkbox.Root>
                    ))}
                  </Flex>
                  <Divider mt={4} />
                </Box>
              ))}
            </Flex>
          )}
        </Card.Body>
      </Card.Root>

      <Flex justify="flex-end" gap={3}>
        <Button variant="surface" onClick={onClose} disabled={isSaving}>
          Cancel
        </Button>
        <Button
          colorPalette="blue"
          onClick={handleSave}
          disabled={isSaving}
          loading={isSaving}
        >
          <LuSave />
          {isNewRole ? "Create Role" : "Save Changes"}
        </Button>
      </Flex>
    </Box>
  );
};

export default RoleDetail;
