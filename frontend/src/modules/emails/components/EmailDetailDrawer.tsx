import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Alert, Badge, Button, Select } from "../../../shared/ui";
import { updateEmailStatus } from "../api/emails.api";
import type { EmailStatus, JobEmail } from "../types/emails.types";

const STATUS_LABELS: Record<EmailStatus, string> = {
  candidature: "Candidature envoyée",
  accuse_reception: "Accusé de réception",
  entretien: "Entretien",
  refus: "Refus",
  recruteur_contact: "Contact recruteur",
  suivi: "Suivi",
  inconnu: "Inconnu",
};

const STATUS_BADGE: Record<EmailStatus, "success" | "warning" | "danger" | "neutral"> = {
  candidature: "success",
  accuse_reception: "neutral",
  entretien: "warning",
  refus: "danger",
  recruteur_contact: "warning",
  suivi: "neutral",
  inconnu: "neutral",
};

const ALL_STATUSES: EmailStatus[] = [
  "candidature",
  "accuse_reception",
  "entretien",
  "refus",
  "recruteur_contact",
  "suivi",
  "inconnu",
];

type EmailDetailDrawerProps = {
  email: JobEmail | null;
  onClose: () => void;
  onStatusUpdated: (updated: JobEmail) => void;
};

export function EmailDetailDrawer({ email, onClose, onStatusUpdated }: EmailDetailDrawerProps) {
  const queryClient = useQueryClient();
  const [statusValue, setStatusValue] = useState<EmailStatus>(email?.status ?? "inconnu");
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Keep local status in sync when a different email is opened
  if (email && statusValue !== email.status && !saveSuccess) {
    setStatusValue(email.status);
  }

  const mutation = useMutation({
    mutationFn: (newStatus: EmailStatus) => updateEmailStatus(email!.id, newStatus),
    onSuccess: (updated) => {
      setSaveSuccess(true);
      onStatusUpdated(updated);
      queryClient.invalidateQueries({ queryKey: ["emails"] });
      queryClient.invalidateQueries({ queryKey: ["emails", "stats"] });
      setTimeout(() => setSaveSuccess(false), 2500);
    },
  });

  if (!email) return null;

  const date = new Date(email.received_at).toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-slate-900/30 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <aside className="fixed inset-y-0 right-0 z-50 flex w-full max-w-xl flex-col overflow-y-auto bg-white shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-4">
          <div className="min-w-0">
            <p className="truncate text-base font-semibold text-slate-900" title={email.subject}>
              {email.subject}
            </p>
            <p className="mt-0.5 text-xs text-slate-500 capitalize">{date}</p>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label="Fermer"
          >
            ✕
          </button>
        </div>

        {/* Meta */}
        <div className="grid grid-cols-2 gap-x-4 gap-y-3 border-b border-slate-100 px-6 py-4 text-sm">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Expéditeur</p>
            <p className="mt-0.5 text-slate-700">
              {email.sender_name ?? email.sender_email ?? <span className="italic text-slate-400">—</span>}
            </p>
            {email.sender_name && email.sender_email && (
              <p className="text-xs text-slate-400">{email.sender_email}</p>
            )}
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Provider</p>
            <p className="mt-0.5 capitalize text-slate-700">{email.provider}</p>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Entreprise</p>
            <p className="mt-0.5 text-slate-700">
              {email.company ?? <span className="italic text-slate-400">—</span>}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Poste</p>
            <p className="mt-0.5 text-slate-700">
              {email.job_title ?? <span className="italic text-slate-400">—</span>}
            </p>
          </div>

          <div className="col-span-2">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Statut actuel</p>
            <div className="mt-1">
              <Badge variant={STATUS_BADGE[email.status]}>
                {STATUS_LABELS[email.status]}
              </Badge>
            </div>
          </div>
        </div>

        {/* Snippet */}
        {email.snippet && (
          <div className="border-b border-slate-100 px-6 py-4">
            <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">Aperçu</p>
            <p className="text-sm leading-relaxed text-slate-600">{email.snippet}</p>
          </div>
        )}

        {/* Body */}
        {email.body_text && (
          <div className="flex-1 border-b border-slate-100 px-6 py-4">
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">Contenu</p>
            <pre className="whitespace-pre-wrap text-xs leading-relaxed text-slate-600 font-sans">
              {email.body_text}
            </pre>
          </div>
        )}

        {/* Status editor */}
        <div className="sticky bottom-0 border-t border-slate-200 bg-white px-6 py-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Corriger le statut
          </p>
          {saveSuccess && (
            <Alert variant="success" className="mb-3">
              Statut mis à jour.
            </Alert>
          )}
          {mutation.isError && (
            <Alert variant="error" className="mb-3">
              Erreur lors de la mise à jour.
            </Alert>
          )}
          <div className="flex items-center gap-3">
            <Select
              value={statusValue}
              onChange={(e) => setStatusValue(e.target.value as EmailStatus)}
              className="flex-1"
            >
              {ALL_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {STATUS_LABELS[s]}
                </option>
              ))}
            </Select>
            <Button
              isLoading={mutation.isPending}
              disabled={statusValue === email.status || mutation.isPending}
              onClick={() => mutation.mutate(statusValue)}
            >
              Enregistrer
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
}
