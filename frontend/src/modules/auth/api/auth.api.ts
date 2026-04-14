import { apiClient } from "../../../shared/api/client";

import type { OAuthLoginResponse, OAuthRouteProviderName, OAuthStatusResponse, ProviderName } from "../types/auth.types";

const oauthRouteByProvider: Record<ProviderName, OAuthRouteProviderName> = {
  gmail: "google",
  outlook: "microsoft",
};

export async function getAuthStatus(): Promise<OAuthStatusResponse> {
  const response = await apiClient.get<OAuthStatusResponse>("/auth/status");
  return response.data;
}

export async function getProviderLoginUrl(provider: ProviderName): Promise<OAuthLoginResponse> {
  const routeProvider = oauthRouteByProvider[provider];
  const response = await apiClient.get<OAuthLoginResponse>(`/auth/${routeProvider}/login`);
  return response.data;
}

export async function disconnectProvider(provider: ProviderName): Promise<void> {
  await apiClient.delete(`/auth/${provider}/disconnect`);
}
