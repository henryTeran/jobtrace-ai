export type DashboardSummary = {
  total: number;
  totalPages: number;
};

export type MonthCount = {
  month: string;
  count: number;
};

export type EmailStats = {
  total: number;
  by_status: Record<string, number>;
  by_provider: Record<string, number>;
  by_month: MonthCount[];
};
