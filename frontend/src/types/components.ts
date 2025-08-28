import type {
  UseFormRegister,
  FieldErrors,
  FieldValues,
} from "react-hook-form";
import type { ApiResponse, RequestDetails } from "./api";
import type { UserState } from "./user";

export type EndpointItemProps = {
  method: string;
  endpoint: string;
  title: string;
  subheader: string;
  access: string;
  args: Array<{ name: string; description: string }>;
  raises: Array<{ name: string; description: string }>;
  returns: Array<{ name: string; description: string }>;
  requestBody: string;
  onBodyChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  endpointId: string;
  expandedEndpoint: string | null;
  onEndpointSelect: (endpointId: string) => void;
  onTryEndpoint: () => void;
  onReset: () => void;
  isLoading: boolean;
  isTested: boolean;
  response: ApiResponse | null;
  requestDetails: RequestDetails;
  urlParams: Record<string, string>;
  onUrlParamChange: (
    endpointId: string,
    paramName: string,
    value: string,
  ) => void;
};

export interface EndpointData {
  id: string;
  method: string;
  endpoint: string;
  title: string;
  subheader: string;
  access: string;
  args: Array<{ name: string; description: string }>;
  raises: Array<{ name: string; description: string }>;
  returns: Array<{ name: string; description: string }>;
  requestBody: string;
  onBodyChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  urlParams: Record<string, string>;
}

export interface EndpointCategoryProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export type AuthFormProps = {
  isSignupMode: boolean;
  onToggleMode: () => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  errors: FieldErrors<FieldValues>;
  isLoading: boolean;
  errorMessage: string;
  register: UseFormRegister<FieldValues>;
};

export interface UserInfoProps {
  user: UserState;
  onLogout: () => void;
}

export interface AuthDialogProps {
  isAuthenticated: boolean;
  user: UserState;
}

export interface LoadingOverlayProps {
  isLoading: boolean;
}
