import React from "react";
import { Flex, Text, Badge, IconButton, Box } from "@chakra-ui/react";
import { LuChevronUp, LuLockOpen, LuLock } from "react-icons/lu";

interface EndpointHeaderProps {
  method: string;
  endpoint: string;
  title: string;
  access: string;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isExpanded: boolean;
  endpointId: string;
  onEndpointSelect: (endpointId: string) => void;
  getBadgeColor: (method: string) => string;
}

const areEqual = (
  prevProps: EndpointHeaderProps,
  nextProps: EndpointHeaderProps,
): boolean => {
  if (prevProps.method !== nextProps.method) return false;
  if (prevProps.endpoint !== nextProps.endpoint) return false;
  if (prevProps.title !== nextProps.title) return false;
  if (prevProps.access !== nextProps.access) return false;
  if (prevProps.isAuthenticated !== nextProps.isAuthenticated) return false;
  if (prevProps.isAdmin !== nextProps.isAdmin) return false;
  if (prevProps.isExpanded !== nextProps.isExpanded) return false;
  if (prevProps.endpointId !== nextProps.endpointId) return false;

  if (prevProps.onEndpointSelect !== nextProps.onEndpointSelect) return false;
  if (prevProps.getBadgeColor !== nextProps.getBadgeColor) return false;

  return true;
};

const EndpointHeader: React.FC<EndpointHeaderProps> = ({
  method,
  endpoint,
  title,
  access,
  isAuthenticated,
  isAdmin,
  isExpanded,
  endpointId,
  onEndpointSelect,
  getBadgeColor,
}) => {
  return (
    <Flex
      p={{ base: 1, sm: 2, md: 3 }}
      alignItems="center"
      justifyContent="space-between"
      cursor="pointer"
      onClick={() => onEndpointSelect(endpointId)}
      id={`endpoint-header`}
      minHeight={{ base: "40px", sm: "48px", md: "56px" }}
      transition="all 0.2s ease"
      _hover={{ bg: "bg.subtle" }}
    >
      <Flex alignItems="center" gap={2}>
        <Badge
          w={{ base: 12, sm: 14, md: 16 }}
          size={{ base: "sm", sm: "md", md: "lg" }}
          colorPalette={getBadgeColor(method)}
          justifyContent="center"
          id={"endpoint-badge"}
        >
          {method}
        </Badge>
        <Text
          fontWeight="bold"
          px={{ base: 2, sm: 3, md: 4, lg: 6 }}
          w={{
            base: "120px",
            sm: "140px",
            md: "200px",
            lg: "280px",
            xl: "320px",
          }}
          fontSize={{ base: "xs", sm: "sm", md: "md" }}
          lineClamp={1}
          flexShrink="0"
          id={"endpoint-url"}
          whiteSpace="nowrap"
          overflow="hidden"
          textOverflow="ellipsis"
        >
          {endpoint}
        </Text>
        <Text
          w={{
            base: "80px",
            sm: "120px",
            md: "200px",
            lg: "300px",
            xl: "400px",
          }}
          fontSize={{ base: "xs", sm: "sm", md: "md" }}
          lineHeight="1.2"
          lineClamp={{ base: 2, md: 1 }}
          overflow="hidden"
          textOverflow="ellipsis"
          flex="1"
          minW="0"
          id={"endpoint-title"}
        >
          {title}
        </Text>
      </Flex>
      <Flex alignItems="center" gap={{ base: 1, sm: 2 }}>
        {access !== "PUBLIC" && (
          <Box display={{ base: "none", sm: "block" }}>
            {!isAuthenticated ? (
              <LuLockOpen color="gray" style={{ opacity: 0.7 }} />
            ) : access === "ADMIN" ? (
              <div>
                {isAdmin ? (
                  <LuLock color="green" style={{ opacity: 0.7 }} />
                ) : (
                  <LuLockOpen
                    color="gray"
                    style={{ opacity: 0.7 }}
                    title="Admin access required"
                  />
                )}
              </div>
            ) : (
              <LuLock color="green" style={{ opacity: 0.7 }} />
            )}
          </Box>
        )}

        <IconButton
          size="sm"
          variant="ghost"
          aria-label={isExpanded ? "Collapse" : "Expand"}
          onClick={() => onEndpointSelect(endpointId)}
          transition="transform 0.2s ease"
          transform={isExpanded ? "rotate(0deg)" : "rotate(180deg)"}
          flexShrink={0}
        >
          <LuChevronUp />
        </IconButton>
      </Flex>
    </Flex>
  );
};

export default React.memo(EndpointHeader, areEqual);
