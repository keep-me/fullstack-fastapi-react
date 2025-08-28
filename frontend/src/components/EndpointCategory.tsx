import {
  Box,
  Flex,
  Heading,
  Collapsible,
  Separator,
  IconButton,
  Text,
} from "@chakra-ui/react";
import { LuChevronUp } from "react-icons/lu";
import { useState } from "react";
import type { EndpointCategoryProps } from "@/types/components";

/**
 * Component for displaying a collapsible category section with endpoints.
 * @param {Object} props - Component properties
 * @param {string} props.title - Category title
 * @param {string} props.subtitle - Category subtitle/description
 * @param {React.ReactNode} props.children - Child components to render inside the category
 * @returns {React.ReactElement} The EndpointCategory component
 */
function EndpointCategory({
  title,
  subtitle,
  children,
}: EndpointCategoryProps): React.ReactElement {
  const [isExpanded, setIsExpanded] = useState(true);

  /**
   * Handles toggle of category expansion state.
   * @returns {void}
   */
  const handleToggle = (): void => {
    setIsExpanded(!isExpanded);
  };

  return (
    <Box mb={8} width="100%" id={`category-section-${title}`}>
      <Collapsible.Root width="100%" defaultOpen={isExpanded} unmountOnExit>
        <Collapsible.Trigger asChild>
          <Flex
            role="button"
            tabIndex={0}
            alignItems="center"
            justifyContent="space-between"
            _hover={{ bg: "bg.subtle" }}
            onClick={handleToggle}
            transition="background-color 0.2s ease"
          >
            <Flex
              p={2}
              width="100%"
              alignItems="center"
              justifyContent="space-between"
              cursor="pointer"
            >
              <Flex flexDirection="column" alignItems="flex-start" gap={2}>
                <Heading size="lg">{title}</Heading>
                <Text fontSize="md" color="gray.500">
                  {subtitle}
                </Text>
              </Flex>
            </Flex>

            <IconButton
              size="sm"
              variant="ghost"
              aria-label={isExpanded ? "Collapse" : "Expand"}
              transition="transform 0.2s ease"
              transform={isExpanded ? "rotate(0deg)" : "rotate(180deg)"}
              mr={{ base: 1, sm: 2, md: 3 }}
            >
              <LuChevronUp />
            </IconButton>
          </Flex>
        </Collapsible.Trigger>
        <Separator
          opacity={isExpanded ? 0 : 1}
          transition="opacity 0.2s ease"
        />
        <Collapsible.Content>
          <Box transition="all 0.3s ease" overflow="hidden">
            {children}
          </Box>
        </Collapsible.Content>
      </Collapsible.Root>
    </Box>
  );
}

export default EndpointCategory;
