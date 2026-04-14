import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../../../shared/api/client";
import type { EmailStats } from "../types/dashboard.types";

async function fetchEmailStats(): Promise<EmailStats> {
  const response = await apiClient.get<EmailStats>("/emails/stats");
  return response.data;
}

export function useEmailStats() {
  return useQuery({
    queryKey: ["emails", "stats"],
    queryFn: fetchEmailStats,
    staleTime: 60_000,
  });
}
