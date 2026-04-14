import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { Alert, Badge, Button, EmptyState, Input, Loader, Select, Table } from "../../../shared/ui";
import { env } from "../../../shared/config/env";
import { exportFilteredEmailsPdf, getAllEmailsForExport } from "../api/emails.api";
import { EmailDetailDrawer } from "../components/EmailDetailDrawer";
import { useEmails } from "../hooks/useEmails";
import type { EmailSortBy, EmailSortOrder, EmailStatus, JobEmail } from "../types/emails.types";

type ExportKind = "csv" | "pdf";

type ExportHistoryEntry = {
  kind: ExportKind;
  filename: string;
  rows: number;
  createdAt: string;
};

const EXPORT_HISTORY_KEY = "jobtrace.emails.exports";

const STATUS_VARIANT: Record<EmailStatus, "success" | "warning" | "danger" | "neutral"> = {
  candidature: "success",
  accuse_reception: "neutral",
  entretien: "warning",
  refus: "danger",
  recruteur_contact: "warning",
  suivi: "neutral",
  inconnu: "neutral",
};

export function EmailsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filtersOpen, setFiltersOpen] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<JobEmail | null>(null);
  const [localItems, setLocalItems] = useState<JobEmail[]>([]);
  const [isExporting, setIsExporting] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);
  const [exportHistory, setExportHistory] = useState<ExportHistoryEntry[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const raw = window.localStorage.getItem(EXPORT_HISTORY_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw) as ExportHistoryEntry[];
      if (!Array.isArray(parsed)) return [];
      return parsed.slice(0, 5);
    } catch {
      return [];
    }
  });

  const page = Number(searchParams.get("page") ?? "1") || 1;
  const pageSize = Number(searchParams.get("pageSize") ?? "20") || 20;
  const provider = (searchParams.get("provider") as "gmail" | "outlook" | null) ?? undefined;
  const status = (searchParams.get("status") as EmailStatus | null) ?? undefined;
  const dateFrom = searchParams.get("dateFrom") ?? undefined;
  const dateTo = searchParams.get("dateTo") ?? undefined;
  const q = searchParams.get("q") ?? undefined;
  const sortBy = (searchParams.get("sortBy") as EmailSortBy | null) ?? "received_at";
  const sortOrder = (searchParams.get("sortOrder") as EmailSortOrder | null) ?? "desc";

  const { data, isLoading, mappedError, isFetching } = useEmails({
    page,
    pageSize,
    provider,
    status,
    q,
    dateFrom,
    dateTo,
    sortBy,
    sortOrder,
  });

  // Merge server items with any local status overrides
  const displayItems = useMemo(() => {
    if (!data) return [];
    return data.items.map((item) => {
      const override = localItems.find((l) => l.id === item.id);
      return override ?? item;
    });
  }, [data, localItems]);

  const handleStatusUpdated = (updated: JobEmail) => {
    setLocalItems((prev) => {
      const exists = prev.some((l) => l.id === updated.id);
      if (exists) return prev.map((l) => (l.id === updated.id ? updated : l));
      return [...prev, updated];
    });
    setSelectedEmail(updated);
  };

  const hasPreviousPage = page > 1;
  const hasNextPage = useMemo(() => {
    if (!data) return false;
    return page < data.pagination.total_pages;
  }, [data, page]);

  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (q) count += 1;
    if (status) count += 1;
    if (provider) count += 1;
    if (dateFrom) count += 1;
    if (dateTo) count += 1;
    if (sortBy !== "received_at") count += 1;
    if (sortOrder !== "desc") count += 1;
    if (pageSize !== 20) count += 1;
    return count;
  }, [q, status, provider, dateFrom, dateTo, sortBy, sortOrder, pageSize]);

  const updateParams = (updates: Record<string, string | undefined>, resetPage = true) => {
    const next = new URLSearchParams(searchParams);

    Object.entries(updates).forEach(([key, value]) => {
      if (!value) {
        next.delete(key);
      } else {
        next.set(key, value);
      }
    });

    if (resetPage) {
      next.set("page", "1");
    }

    if (!next.get("page")) {
      next.set("page", "1");
    }
    if (!next.get("pageSize")) {
      next.set("pageSize", "20");
    }

    setSearchParams(next);
  };

  const goToPage = (nextPage: number) => {
    updateParams({ page: String(nextPage) }, false);
  };

  const resetFilters = () => {
    setSearchParams({ page: "1", pageSize: "20", sortBy: "received_at", sortOrder: "desc" });
  };

  const escapeCsv = (value: string | null | undefined) => {
    const normalized = (value ?? "").replace(/"/g, '""');
    return `"${normalized}"`;
  };

  const toCsv = (items: JobEmail[]) => {
    const header = [
      "id",
      "received_at",
      "provider",
      "status",
      "company",
      "job_title",
      "subject",
      "sender_email",
      "sender_name",
      "snippet",
    ];

    const rows = items.map((item) =>
      [
        String(item.id),
        item.received_at,
        item.provider,
        item.status,
        item.company,
        item.job_title,
        item.subject,
        item.sender_email,
        item.sender_name,
        item.snippet,
      ]
        .map((value) => escapeCsv(value))
        .join(","),
    );

    return [header.join(","), ...rows].join("\n");
  };

  const downloadCsv = (content: string, filename: string) => {
    const blob = new Blob([content], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const addExportHistory = (entry: ExportHistoryEntry) => {
    const nextHistory: ExportHistoryEntry[] = [entry, ...exportHistory].slice(0, 5);
    setExportHistory(nextHistory);
    window.localStorage.setItem(EXPORT_HISTORY_KEY, JSON.stringify(nextHistory));
  };

  const onExportCsv = async () => {
    setIsExporting(true);
    setExportError(null);
    setExportSuccess(null);
    try {
      const allItems = await getAllEmailsForExport({
        provider,
        status,
        q,
        dateFrom,
        dateTo,
        sortBy,
        sortOrder,
      });

      const now = new Date();
      const timestamp = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
      const filename = `emails_filtered_${timestamp}.csv`;
      const csv = toCsv(allItems);
      downloadCsv(csv, filename);
      setExportSuccess(`Export CSV termine (${allItems.length} lignes).`);
      addExportHistory({
        kind: "csv",
        filename,
        rows: allItems.length,
        createdAt: new Date().toISOString(),
      });
    } catch {
      setExportError("Export CSV impossible pour le moment. Reessaie dans quelques secondes.");
    } finally {
      setIsExporting(false);
    }
  };

  const onExportPdf = async () => {
    setIsExportingPdf(true);
    setExportError(null);
    setExportSuccess(null);
    try {
      const result = await exportFilteredEmailsPdf({
        provider,
        status,
        q,
        dateFrom,
        dateTo,
        sortBy,
        sortOrder,
      });

      const filename = result.file_path.split("/").pop();
      if (!filename) {
        setExportError("Le serveur a genere un PDF, mais le nom du fichier est invalide.");
        return;
      }

      const downloadUrl = `${env.apiBaseUrl}/reports/files/${encodeURIComponent(filename)}`;
      window.open(downloadUrl, "_blank", "noopener,noreferrer");
      setExportSuccess(`Export PDF termine (${result.rows} lignes).`);
      addExportHistory({
        kind: "pdf",
        filename,
        rows: result.rows,
        createdAt: new Date().toISOString(),
      });
    } catch {
      setExportError("Export PDF impossible pour le moment. Reessaie dans quelques secondes.");
    } finally {
      setIsExportingPdf(false);
    }
  };

  return (
    <main className="space-y-6 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-slate-900">Emails</h1>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={() => setFiltersOpen((value) => !value)}>
            {filtersOpen ? "Masquer filtres" : "Afficher filtres"}
            {activeFiltersCount > 0 ? ` (${activeFiltersCount})` : ""}
          </Button>
          <Button variant="primary" onClick={onExportCsv} isLoading={isExporting}>
            Export CSV
          </Button>
          <Button variant="secondary" onClick={onExportPdf} isLoading={isExportingPdf}>
            Export PDF
          </Button>
          {isFetching ? <span className="text-sm text-slate-500">Mise a jour...</span> : null}
        </div>
      </div>

      {exportError ? <Alert variant="error">{exportError}</Alert> : null}
      {exportSuccess ? <Alert variant="success">{exportSuccess}</Alert> : null}

      {exportHistory.length > 0 ? (
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Derniers exports</p>
          <div className="space-y-1 text-sm text-slate-700">
            {exportHistory.map((entry) => (
              <div key={`${entry.kind}-${entry.createdAt}`} className="flex items-center justify-between gap-3">
                <span>
                  <span className="font-medium">{entry.kind.toUpperCase()}</span>{" "}
                  — {entry.filename} — {entry.rows} lignes —{" "}
                  {new Date(entry.createdAt).toLocaleString("fr-FR")}
                </span>
                {entry.kind === "pdf" && (
                  <a
                    href={`${env.apiBaseUrl}/reports/files/${encodeURIComponent(entry.filename)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="shrink-0 text-xs font-medium text-teal-700 hover:underline"
                  >
                    Ouvrir
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {filtersOpen ? (
        <div className="grid gap-3 rounded-lg border border-slate-200 bg-white p-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Recherche</label>
            <Input
              value={q ?? ""}
              placeholder="Sujet, entreprise, poste..."
              onChange={(event) => updateParams({ q: event.target.value || undefined })}
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Statut</label>
            <Select value={status ?? ""} onChange={(event) => updateParams({ status: event.target.value || undefined })}>
              <option value="">Tous</option>
              <option value="candidature">candidature</option>
              <option value="accuse_reception">accuse_reception</option>
              <option value="entretien">entretien</option>
              <option value="refus">refus</option>
              <option value="recruteur_contact">recruteur_contact</option>
              <option value="suivi">suivi</option>
              <option value="inconnu">inconnu</option>
            </Select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Source</label>
            <Select
              value={provider ?? ""}
              onChange={(event) => updateParams({ provider: event.target.value || undefined })}
            >
              <option value="">Toutes</option>
              <option value="gmail">gmail</option>
              <option value="outlook">outlook</option>
            </Select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Taille page</label>
            <Select
              value={String(pageSize)}
              onChange={(event) => updateParams({ pageSize: event.target.value || "20" })}
            >
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </Select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Date debut</label>
            <Input
              type="date"
              value={dateFrom ?? ""}
              onChange={(event) => updateParams({ dateFrom: event.target.value || undefined })}
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Date fin</label>
            <Input type="date" value={dateTo ?? ""} onChange={(event) => updateParams({ dateTo: event.target.value || undefined })} />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Tri</label>
            <Select value={sortBy} onChange={(event) => updateParams({ sortBy: event.target.value as EmailSortBy })}>
              <option value="received_at">Date reception</option>
              <option value="created_at">Date insertion</option>
              <option value="company">Entreprise</option>
              <option value="status">Statut</option>
              <option value="provider">Source</option>
              <option value="subject">Sujet</option>
            </Select>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">Ordre</label>
            <div className="flex gap-2">
              <Select value={sortOrder} onChange={(event) => updateParams({ sortOrder: event.target.value as EmailSortOrder })}>
                <option value="desc">desc</option>
                <option value="asc">asc</option>
              </Select>
              <Button variant="ghost" onClick={resetFilters}>
                Reset
              </Button>
            </div>
          </div>
        </div>
      ) : null}

      {activeFiltersCount > 0 ? (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Filtres actifs</span>
          {q ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ q: undefined })}
            >
              Recherche: {q}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
          {status ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ status: undefined })}
            >
              Statut: {status}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
          {provider ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ provider: undefined })}
            >
              Source: {provider}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
          {dateFrom ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ dateFrom: undefined })}
            >
              Debut: {dateFrom}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
          {dateTo ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ dateTo: undefined })}
            >
              Fin: {dateTo}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
          {sortBy !== "received_at" ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ sortBy: "received_at" })}
            >
              Tri: {sortBy}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
          {sortOrder !== "desc" ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ sortOrder: "desc" })}
            >
              Ordre: {sortOrder}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
          {pageSize !== 20 ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-3 py-1 text-xs text-slate-700 hover:bg-slate-50"
              onClick={() => updateParams({ pageSize: "20" })}
            >
              Taille: {pageSize}
              <span aria-hidden="true">x</span>
            </button>
          ) : null}
        </div>
      ) : null}

      {isLoading ? (
        <Loader />
      ) : mappedError ? (
        <Alert variant="error">{mappedError.message}</Alert>
      ) : !data || data.items.length === 0 ? (
        <EmptyState title="Aucun email" description="Lance une synchronisation pour recuperer des emails traites." />
      ) : (
        <>
          <Table>
            <thead className="bg-slate-100 text-xs uppercase text-slate-600">
              <tr>
                <th className="px-3 py-2">Date</th>
                <th className="px-3 py-2">Entreprise</th>
                <th className="px-3 py-2">Sujet</th>
                <th className="px-3 py-2">Statut</th>
                <th className="px-3 py-2">Source</th>
              </tr>
            </thead>
            <tbody>
              {displayItems.map((item) => (
                <tr
                  key={item.id}
                  className="cursor-pointer border-t border-slate-200 hover:bg-slate-50"
                  onClick={() => setSelectedEmail(item)}
                >
                  <td className="px-3 py-2 text-sm text-slate-700">{new Date(item.received_at).toLocaleDateString("fr-FR")}</td>
                  <td className="px-3 py-2 text-sm text-slate-900">{item.company ?? "-"}</td>
                  <td className="px-3 py-2 text-sm text-slate-700 max-w-xs truncate" title={item.subject}>{item.subject}</td>
                  <td className="px-3 py-2">
                    <Badge variant={STATUS_VARIANT[item.status]}>{item.status}</Badge>
                  </td>
                  <td className="px-3 py-2 text-sm text-slate-700 capitalize">{item.provider}</td>
                </tr>
              ))}
            </tbody>
          </Table>

          <div className="flex items-center justify-between gap-3">
            <p className="text-sm text-slate-600">
              Page {data.pagination.page} / {data.pagination.total_pages} ({data.pagination.total} elements)
            </p>
            <div className="flex items-center gap-2">
              <Button variant="secondary" disabled={!hasPreviousPage} onClick={() => goToPage(page - 1)}>
                Precedent
              </Button>
              <Button variant="secondary" disabled={!hasNextPage} onClick={() => goToPage(page + 1)}>
                Suivant
              </Button>
            </div>
          </div>
        </>
      )}

      <EmailDetailDrawer
        email={selectedEmail}
        onClose={() => setSelectedEmail(null)}
        onStatusUpdated={handleStatusUpdated}
      />
    </main>
  );
}
