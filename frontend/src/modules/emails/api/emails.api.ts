import { apiClient } from "../../../shared/api/client";

import type { EmailListResponse, GetEmailsParams, JobEmail } from "../types/emails.types";

type PdfExportResponse = {
  file_path: string;
  months: string[];
  rows: number;
};

export async function getEmails({
  page,
  pageSize,
  provider,
  status,
  q,
  dateFrom,
  dateTo,
  sortBy = "received_at",
  sortOrder = "desc",
}: GetEmailsParams): Promise<EmailListResponse> {
  const response = await apiClient.get<EmailListResponse>("/emails", {
    params: {
      page,
      page_size: pageSize,
      provider,
      status,
      q,
      date_from: dateFrom ? `${dateFrom}T00:00:00` : undefined,
      date_to: dateTo ? `${dateTo}T23:59:59` : undefined,
      sort_by: sortBy,
      sort_order: sortOrder,
    },
  });

  return response.data;
}

export async function getAllEmailsForExport(params: Omit<GetEmailsParams, "page" | "pageSize">): Promise<JobEmail[]> {
  const firstPage = await getEmails({
    ...params,
    page: 1,
    pageSize: 200,
  });

  const items = [...firstPage.items];
  const totalPages = firstPage.pagination.total_pages;

  if (totalPages <= 1) {
    return items;
  }

  const pageRequests: Array<Promise<EmailListResponse>> = [];
  for (let page = 2; page <= totalPages; page += 1) {
    pageRequests.push(
      getEmails({
        ...params,
        page,
        pageSize: 200,
      }),
    );
  }

  const pages = await Promise.all(pageRequests);
  for (const pageData of pages) {
    items.push(...pageData.items);
  }

  return items;
}

export async function exportFilteredEmailsPdf(params: Omit<GetEmailsParams, "page" | "pageSize">): Promise<PdfExportResponse> {
  const response = await apiClient.post<PdfExportResponse>("/reports/pdf/filtered", {
    provider: params.provider,
    status: params.status,
    q: params.q,
    date_from: params.dateFrom ? `${params.dateFrom}T00:00:00` : undefined,
    date_to: params.dateTo ? `${params.dateTo}T23:59:59` : undefined,
    sort_by: params.sortBy ?? "received_at",
    sort_order: params.sortOrder ?? "desc",
  });

  return response.data;
}

export async function updateEmailStatus(emailId: number, status: string): Promise<JobEmail> {
  const response = await apiClient.patch<JobEmail>(`/emails/${emailId}/status`, { status });
  return response.data;
}
