export type EmailStatus =
  | "candidature"
  | "accuse_reception"
  | "entretien"
  | "refus"
  | "recruteur_contact"
  | "suivi"
  | "inconnu";

export type JobEmail = {
  id: number;
  provider: string;
  message_id: string;
  thread_id: string | null;
  subject: string;
  sender_email: string | null;
  sender_name: string | null;
  received_at: string;
  month_key: string;
  company: string | null;
  job_title: string | null;
  status: EmailStatus;
  snippet: string | null;
  body_text: string | null;
};

export type PaginationMeta = {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

export type EmailSortBy = "received_at" | "created_at" | "company" | "status" | "provider" | "subject";

export type EmailSortOrder = "asc" | "desc";

export type GetEmailsParams = {
  page: number;
  pageSize: number;
  provider?: "gmail" | "outlook";
  status?: EmailStatus;
  q?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: EmailSortBy;
  sortOrder?: EmailSortOrder;
};

export type EmailListResponse = {
  items: JobEmail[];
  pagination: PaginationMeta;
};
