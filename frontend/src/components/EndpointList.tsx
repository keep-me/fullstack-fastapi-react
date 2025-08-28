import React, { Suspense, lazy } from "react";
import { Box, Spinner, Text, Flex } from "@chakra-ui/react";
import {
  ENDPOINT_IDS,
  ENDPOINT_CATEGORIES,
} from "@/constants/endpointConstants";

const CategorySection = lazy(() => import("./CategorySection"));

const CategoryLoadingFallback = ({ title }: { title: string }) => (
  <Box maxW="1200px" mx="auto" p={5}>
    <Flex align="center" gap={3} p={4} borderRadius="md" bg="bg.muted">
      <Spinner size="sm" />
      <Text fontSize="lg" fontWeight="bold" color="gray.500">
        Loading {title} endpoints...
      </Text>
    </Flex>
  </Box>
);

const EndpointList: React.FC = () => {
  const othersEndpoints = [ENDPOINT_IDS.HEALTH];

  const authEndpoints = [
    ENDPOINT_IDS.AUTH_SIGNUP,
    ENDPOINT_IDS.AUTH_LOGIN,
    ENDPOINT_IDS.AUTH_REFRESH,
    ENDPOINT_IDS.AUTH_LOGOUT,
    ENDPOINT_IDS.AUTH_RESET_PASSWORD,
    ENDPOINT_IDS.AUTH_VERIFY_CODE,
    ENDPOINT_IDS.AUTH_NEW_PASSWORD,
  ];

  const usersEndpoints = [
    ENDPOINT_IDS.USERS_ME,
    ENDPOINT_IDS.USERS_MY_ID,
    ENDPOINT_IDS.USERS_UPDATE_ME,
    ENDPOINT_IDS.USERS_UPDATE_PASSWORD,
    ENDPOINT_IDS.USERS_DELETE_ME,
    ENDPOINT_IDS.USERS_CREATE,
    ENDPOINT_IDS.USERS_LIST,
    ENDPOINT_IDS.USERS_BY_ID,
    ENDPOINT_IDS.USERS_UPDATE_BY_ID,
    ENDPOINT_IDS.USERS_DELETE_BY_ID,
  ];

  return (
    <>
      <Suspense
        fallback={
          <CategoryLoadingFallback title={ENDPOINT_CATEGORIES.OTHERS.title} />
        }
      >
        <CategorySection
          title={ENDPOINT_CATEGORIES.OTHERS.title}
          subtitle={ENDPOINT_CATEGORIES.OTHERS.subtitle}
          endpointIds={othersEndpoints}
        />
      </Suspense>

      <Suspense
        fallback={
          <CategoryLoadingFallback title={ENDPOINT_CATEGORIES.AUTH.title} />
        }
      >
        <CategorySection
          title={ENDPOINT_CATEGORIES.AUTH.title}
          subtitle={ENDPOINT_CATEGORIES.AUTH.subtitle}
          endpointIds={authEndpoints}
        />
      </Suspense>

      <Suspense
        fallback={
          <CategoryLoadingFallback title={ENDPOINT_CATEGORIES.USERS.title} />
        }
      >
        <CategorySection
          title={ENDPOINT_CATEGORIES.USERS.title}
          subtitle={ENDPOINT_CATEGORIES.USERS.subtitle}
          endpointIds={usersEndpoints}
        />
      </Suspense>
    </>
  );
};

export default React.memo(EndpointList);
