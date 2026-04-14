import { useState } from "react";

import { Alert, Badge, Button, Card, Loader } from "../../../shared/ui";
import { env } from "../../../shared/config/env";
import { useMonthlyReport } from "../hooks/useMonthlyReport";
import type { JobEmail } from "../../emails/types/emails.types";
import { generateMonthPdf } from "../api/reports.api";

const STATUS_LABELS: Record<string, string> = {
  candidature: "Candidature",
  accuse_reception: "Accusé réception",
  entretien: "Entretien",
  refus: "Refus",
  recruteur_contact: "Contact recruteur",
  suivi: "Suivi",
  inconnu: "Inconnu",
};

const STATUS_BADGE: Record<string, "success" | "warning" | "danger" | "neutral"> = {
  candidature: "neutral",
  accuse_reception: "neutral",
  entretien: "success",
  refus: "danger",
  recruteur_contact: "warning",
  suivi: "warning",
  inconnu: "neutral",
};

function statusBadgeVariant(status: string): "success" | "warning" | "danger" | "neutral" {
  return STATUS_BADGE[status] ?? "neutral";
}

function MonthSection({ month, emails }: { month: string; emails: JobEmail[] }) {
  const [open, setOpen] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  const statusCounts = emails.reduce<Record<string, number>>((acc, e) => {
    acc[e.status] = (acc[e.status] ?? 0) + 1;
    return acc;
  }, {});

  const [year, monthNum] = month.split("-");
  const label = new Date(Number(year), Number(monthNum) - 1).toLocaleDateString("fr-FR", {
    month: "long",
    year: "numeric",
  });

  async function handleExportPdf() {
    setExporting(true);
    setPdfError(null);
    try {
      const result = await generateMonthPdf([month]);
      const filename = result.file_path.split("/").pop()!;
      window.open(`${env.apiBaseUrl}/reports/files/${encodeURIComponent(filename)}`, "_blank");
    } catch {
      setPdfError("Erreur lors de la génération du PDF.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <Card className="overflow-hidden p-0">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 px-5 py-4">
        <button
          className="flex flex-1 items-center gap-3 text-left"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
        >
          <span className="text-base font-semibold text-slate-900 capitalize">{label}</span>
          <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
            {emails.length} email{emails.length > 1 ? "s" : ""}
          </span>
          <span className="ml-auto text-slate-400">{open ? "▲" : "▼"}</span>
        </button>

        <div className="flex items-center gap-2 flex-shrink-0">
          {Object.entries(statusCounts)
            .sort(([, a], [, b]) => b - a)
            .map(([status, count]) => (
              <Badge key={status} variant={statusBadgeVariant(status)}>
                {STATUS_LABELS[status] ?? status} {count}
              </Badge>
            ))}
          <Button className="px-3 py-1.5 text-xs" variant="secondary" onClick={handleExportPdf} disabled={exporting}>
            {exporting ? "Export…" : "PDF"}
          </Button>
        </div>
      </div>

      {pdfError && (
        <div className="px-5 pb-3">
          <Alert variant="error">{pdfError}</Alert>
        </div>
      )}

      {/* Email rows */}
      {open && (
        <div className="border-t border-slate-100">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-2 text-left">Date</th>
                <th className="px-4 py-2 text-left">Sujet</th>
                <th className="px-4 py-2 text-left">Entreprise</th>
                <th className="px-4 py-2 text-left">Statut</th>
                <th className="px-4 py-2 text-left">Provider</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {emails.map((email) => (
                <tr key={email.id} className="hover:bg-slate-50">
                  <td className="px-4 py-2.5 text-slate-500 whitespace-nowrap">
                    {new Date(email.received_at).toLocaleDateString("fr-FR")}
                  </td>
                  <td className="px-4 py-2.5 text-slate-800 max-w-xs truncate" title={email.subject}>
                    {email.subject}
                  </td>
                  <td className="px-4 py-2.5 text-slate-600 max-w-xs truncate">
                    {email.company ?? <span className="text-slate-400 italic">—</span>}
                  </td>
                  <td className="px-4 py-2.5">
                    <Badge variant={statusBadgeVariant(email.status)}>
                      {STATUS_LABELS[email.status] ?? email.status}
                    </Badge>
                  </td>
                  <td className="px-4 py-2.5 text-slate-500 capitalize">{email.provider}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

export function ReportsPage() {
  const [page, setPage] = useState(1);
  const PAGE_SIZE = 200;

  const { data, isLoading, isError } = useMonthlyReport({
    page,
    pageSize: PAGE_SIZE,
    sortBy: "received_at",
    sortOrder: "desc",
  });

  const months = data ? Object.keys(data.data).sort((a, b) => b.localeCompare(a)) : [];
  const totalPages = data?.pagination.total_pages ?? 1;

  return (
    <main className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Rapports mensuels</h1>
          {data && (
            <p className="mt-1 text-sm text-slate-500">
              {data.pagination.total} email{data.pagination.total > 1 ? "s" : ""} au total
            </p>
          )}
        </div>
      </div>

      {isLoading && (
        <div className="flex justify-center py-12">
          <Loader />
        </div>
      )}

      {isError && (
        <Alert variant="error">Impossible de charger les rapports. Vérifie que le serveur est actif.</Alert>
      )}

      {!isLoading && !isError && months.length === 0 && (
        <div className="rounded-lg border border-dashed border-slate-300 py-16 text-center text-slate-500">
          Aucun email synchronisé. Lance une synchronisation d'abord.
        </div>
      )}

      <div className="space-y-4">
        {months.map((month) => (
          <MonthSection key={month} month={month} emails={data!.data[month]} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-2">
          <Button variant="secondary" className="px-3 py-1.5 text-xs" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            ← Précédent
          </Button>
          <span className="text-sm text-slate-600">
            Page {page} / {totalPages}
          </span>
          <Button variant="secondary" className="px-3 py-1.5 text-xs" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
            Suivant →
          </Button>
        </div>
      )}
    </main>
  );
}

