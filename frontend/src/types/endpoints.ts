export interface EndpointArg {
  name: string;
  description: string;
}

export interface EndpointRaise {
  name: string;
  description: string;
}

export interface EndpointReturn {
  name: string;
  description: string;
}

export type EndpointConfig = {
  method: string;
  path: string;
  title: string;
  subheader: string;
  access: string;
  args?: Array<{ name: string; description: string }>;
  raises?: Array<{ name: string; description: string }>;
  returns?: Array<{ name: string; description: string }>;
  defaultBody: string;
  headers: () => Record<string, string>;
  urlParams?: Record<string, string>;
};
