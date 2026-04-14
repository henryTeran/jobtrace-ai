import { apiClient } from "../../../shared/api/client";

import type { GetMonthlyReportParams, MonthlyReportResponse } from "../types/reports.types";

export async function getMonthlyReport(params: GetMonthlyReportParams): Promise<MonthlyReportResponse> {
  const response = await apiClient.get<MonthlyReportResponse>("/reports/monthly", {
    params: {
      months: params.months,
      page: params.page,
      page_size: params.pageSize,
      sort_by: params.sortBy ?? "received_at",
      sort_order: params.sortOrder ?? "desc",
    },
  });
  return response.data;
}

export async function generateMonthPdf(months: string[]): Promise<{ file_path: string }> {
  const response = await apiClient.post<{ file_path: string; months: string[]; rows: number }>("/reports/pdf", {
    months,
  });
  return response.data;
}
