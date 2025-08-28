export interface ApiError {
  message: string;
  status: number;
}

export type ExtendedApiError = {
  status?: number;
  data?: {
    message?: string;
  };
  message?: string;
};

export type QueryArg = {
  url: string;
  method?: string;
  body?: unknown;
  params?: Record<string, unknown>;
  headers?: Record<string, string>;
};

export type RequestDetails = {
  url: string;
  method: string;
  headers: Record<string, string>;
  body: string | null;
};

export type ApiResponse = {
  status: number;
  statusText: string;
  data: unknown;
  headers: Record<string, string>;
  error?: string;
};
