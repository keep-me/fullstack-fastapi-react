import { Box, Button, Flex, Grid, Heading, Text } from "@chakra-ui/react";
import { useState } from "react";
import { LuLock, LuEye, LuChevronUp } from "react-icons/lu";
import { useAppSelector } from "@/redux/hooks";
import RoleList from "./RoleList";
import RoleDetail from "./RoleDetail";
import type { Role } from "@/types/role";

const RoleManagement: React.FC = () => {
  const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);
  const user = useAppSelector((state) => state.user);
  const isAdmin = user.role === "ADMIN";

  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const handleSelectRole = (role: Role) => {
    setSelectedRole(role);
    setIsCreating(false);
  };

  const handleCreateRole = () => {
    setSelectedRole(null);
    setIsCreating(true);
  };

  const handleCloseDetail = () => {
    setSelectedRole(null);
    setIsCreating(false);
  };

  const handleSaved = () => {
    setSelectedRole(null);
    setIsCreating(false);
  };

  if (!isAuthenticated) {
    return (
      <Box p={8} textAlign="center">
        <LuLock size={48} style={{ margin: "0 auto", marginBottom: 16 }} />
        <Heading size="lg" mb={4}>Role Management</Heading>
        <Text color="gray.500">Please log in to access role management.</Text>
      </Box>
    );
  }

  if (!isAdmin) {
    return (
      <Box p={8} textAlign="center">
        <LuLock size={48} style={{ margin: "0 auto", marginBottom: 16, color: "gray.400" }} />
        <Heading size="lg" mb={4}>Access Denied</Heading>
        <Text color="gray.500">
          You need administrator privileges to access role management.
        </Text>
      </Box>
    );
  }

  return (
    <Box maxW="1400px" mx="auto" p={5}>
      <Flex justify="space-between" align="center" mb={6}>
        <Flex align="center" gap={3}>
          <LuLock size={32} />
          <Box>
            <Heading size="lg">Role Management</Heading>
            <Text fontSize="sm" color="gray.500">
              Manage roles and permissions for your application
            </Text>
          </Box>
        </Flex>
        <Button
          colorPalette="blue"
          onClick={handleCreateRole}
          leftIcon={<LuChevronUp />}
        >
          Create Role
        </Button>
      </Flex>

      <Grid
        templateColumns={{
          base: "1fr",
          lg: selectedRole || isCreating ? "1fr 1fr" : "1fr",
        }}
        gap={6}
      >
        <Box
          display={selectedRole || isCreating ? { base: "none", lg: "block" } : "block"}
        >
          <RoleList
            onSelectRole={handleSelectRole}
            selectedRoleId={selectedRole?.id || null}
          />
        </Box>

        {(selectedRole || isCreating) && (
          <Box>
            <RoleDetail
              roleId={isCreating ? null : selectedRole?.id || null}
              onClose={handleCloseDetail}
              onSaved={handleSaved}
            />
          </Box>
        )}
      </Grid>

      {!selectedRole && !isCreating && (
        <Box
          mt={8}
          p={8}
          textAlign="center"
          borderWidth="1px"
          borderRadius="lg"
          borderStyle="dashed"
        >
          <LuEye size={48} style={{ margin: "0 auto", marginBottom: 16, color: "gray.400" }} />
          <Text color="gray.500">
            Select a role from the list to view and edit its details,
            or create a new role.
          </Text>
        </Box>
      )}
    </Box>
  );
};

export default RoleManagement;
