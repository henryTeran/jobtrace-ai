import { useQuery } from "@tanstack/react-query";

import { mapAxiosError } from "../../../shared/api/errors";
import { getDashboardSummary } from "../api/dashboard.api";

export function useDashboardSummary() {
  const query = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: getDashboardSummary,
  });

  return {
    ...query,
    mappedError: query.error ? mapAxiosError(query.error) : null,
  };
}
