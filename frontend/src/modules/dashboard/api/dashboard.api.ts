import { apiClient } from "../../../shared/api/client";

import type { DashboardSummary } from "../types/dashboard.types";

type MonthlyReportResponse = {
  pagination: {
    total: number;
    total_pages: number;
  };
};

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const response = await apiClient.get<MonthlyReportResponse>("/reports/monthly", {
    params: { page: 1, page_size: 1 },
  });

  return {
    total: response.data.pagination.total,
    totalPages: response.data.pagination.total_pages,
  };
}
