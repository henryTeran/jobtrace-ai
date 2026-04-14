import type { JobEmail, PaginationMeta } from "../../emails/types/emails.types";

export type MonthlyReportData = Record<string, JobEmail[]>;

export type MonthlyReportResponse = {
  data: MonthlyReportData;
  pagination: PaginationMeta;
};

export type GetMonthlyReportParams = {
  months?: string[];
  page: number;
  pageSize: number;
  sortBy?: "received_at" | "created_at" | "company" | "status" | "provider" | "subject";
  sortOrder?: "asc" | "desc";
};
