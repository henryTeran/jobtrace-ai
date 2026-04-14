import { useMemo } from "react";

import { useQuery } from "@tanstack/react-query";

import { mapAxiosError } from "../../../shared/api/errors";
import { getAuthStatus } from "../api/auth.api";

export function useAuthStatus() {
  const query = useQuery({
    queryKey: ["auth", "status"],
    queryFn: getAuthStatus,
    refetchInterval: 20_000,
  });

  const summary = useMemo(() => {
    const providers = query.data?.providers ?? [];
    const connectedProviders = providers.filter((provider) => provider.connected).map((provider) => provider.provider);

    return {
      isConnected: connectedProviders.length > 0,
      connectedProviders,
    };
  }, [query.data]);

  return {
    ...query,
    summary,
    mappedError: query.error ? mapAxiosError(query.error) : null,
  };
}
