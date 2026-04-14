import { useQuery } from "@tanstack/react-query";

import { getMonthlyReport } from "../api/reports.api";
import type { GetMonthlyReportParams } from "../types/reports.types";

export function useMonthlyReport(params: GetMonthlyReportParams) {
  return useQuery({
    queryKey: ["reports", "monthly", params],
    queryFn: () => getMonthlyReport(params),
    staleTime: 60_000,
  });
}
