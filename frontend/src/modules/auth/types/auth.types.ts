export type ProviderName = "gmail" | "outlook";
export type OAuthRouteProviderName = "google" | "microsoft";

export type OAuthLoginResponse = {
  auth_url: string;
  state: string;
};

export type ProviderStatus = {
  provider: ProviderName;
  connected: boolean;
  updated_at: string | null;
};

export type OAuthStatusResponse = {
  providers: ProviderStatus[];
};

export type AuthConnectionSummary = {
  isConnected: boolean;
  connectedProviders: ProviderName[];
};
