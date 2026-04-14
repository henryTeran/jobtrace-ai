import { Link } from "react-router-dom";

import { Alert, Badge, Card, Loader } from "../../../shared/ui";
import { useEmailStats } from "../hooks/useEmailStats";

const STATUS_LABELS: Record<string, string> = {
  candidature: "Candidatures",
  accuse_reception: "Accusés réception",
  entretien: "Entretiens",
  refus: "Refus",
  recruteur_contact: "Contacts recruteur",
  suivi: "Suivis",
  inconnu: "Inconnus",
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

// Ordre d'affichage des statuts dans les KPI cards
const STATUS_ORDER = ["candidature", "entretien", "refus", "accuse_reception", "recruteur_contact", "suivi", "inconnu"];

function KpiCard({ label, value, sub }: { label: string; value: number; sub?: string }) {
  return (
    <Card className="flex flex-col gap-1">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="text-3xl font-bold text-slate-900">{value.toLocaleString("fr-FR")}</p>
      {sub && <p className="text-xs text-slate-400">{sub}</p>}
    </Card>
  );
}

function MonthBar({ month, count, max }: { month: string; count: number; max: number }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0;
  const [year, monthNum] = month.split("-");
  const label = new Date(Number(year), Number(monthNum) - 1).toLocaleDateString("fr-FR", { month: "short", year: "2-digit" });

  return (
    <div className="flex items-end gap-1.5">
      <div className="flex flex-col items-center gap-1">
        <span className="text-xs font-medium text-slate-700">{count}</span>
        <div
          className="w-8 rounded-t bg-teal-500 transition-all"
          style={{ height: `${Math.max(pct, 4)}px`, maxHeight: "80px" }}
          title={`${label} : ${count}`}
        />
        <span className="text-xs text-slate-500">{label}</span>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { data, isLoading, isError } = useEmailStats();

  if (isLoading) {
    return (
      <main className="p-6">
        <Loader />
      </main>
    );
  }

  if (isError) {
    return (
      <main className="p-6">
        <Alert variant="error">Impossible de charger les statistiques. Vérifie que le serveur est actif.</Alert>
      </main>
    );
  }

  if (!data || data.total === 0) {
    return (
      <main className="space-y-6 p-6">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <div className="rounded-lg border border-dashed border-slate-300 py-16 text-center">
          <p className="text-slate-500">Aucune donnée synchronisée.</p>
          <Link to="/sync" className="mt-3 inline-block text-sm font-medium text-teal-700 hover:underline">
            Lancer une synchronisation →
          </Link>
        </div>
      </main>
    );
  }

  const maxMonthCount = Math.max(...(data.by_month.map((m) => m.count) ?? [1]), 1);

  return (
    <main className="space-y-8 p-6">
      <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>

      {/* KPI total + providers */}
      <section className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <KpiCard label="Total emails" value={data.total} />
        {Object.entries(data.by_provider).map(([provider, count]) => (
          <KpiCard
            key={provider}
            label={provider.charAt(0).toUpperCase() + provider.slice(1)}
            value={count}
            sub={`${Math.round((count / data.total) * 100)}% du total`}
          />
        ))}
      </section>

      {/* KPI par statut */}
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Par statut</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {STATUS_ORDER.filter((s) => s in data.by_status).map((status) => (
            <Card key={status} className="flex items-center gap-3 p-4">
              <Badge variant={STATUS_BADGE[status] ?? "neutral"}>
                {data.by_status[status]}
              </Badge>
              <span className="text-sm text-slate-700">{STATUS_LABELS[status] ?? status}</span>
            </Card>
          ))}
        </div>
      </section>

      {/* Tendance mensuelle */}
      {data.by_month.length > 0 && (
        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Tendance ({data.by_month.length} dernier{data.by_month.length > 1 ? "s" : ""} mois)
          </h2>
          <Card>
            <div className="flex items-end gap-2 overflow-x-auto pb-2" style={{ minHeight: "120px" }}>
              {data.by_month.map((m) => (
                <MonthBar key={m.month} month={m.month} count={m.count} max={maxMonthCount} />
              ))}
            </div>
          </Card>
        </section>
      )}

      {/* Liens rapides */}
      <section className="flex gap-4">
        <Link to="/emails" className="text-sm font-medium text-teal-700 hover:underline">
          Voir tous les emails →
        </Link>
        <Link to="/reports" className="text-sm font-medium text-teal-700 hover:underline">
          Rapports mensuels →
        </Link>
      </section>
    </main>
  );
}

