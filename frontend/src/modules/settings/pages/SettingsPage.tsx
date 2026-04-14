import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Alert, Badge, Button, Card } from "../../../shared/ui";
import { disconnectProvider, getProviderLoginUrl } from "../../auth/api/auth.api";
import { useAuthStatus } from "../../auth/hooks/useAuthStatus";
import type { ProviderName } from "../../auth/types/auth.types";

const PROVIDER_LABELS: Record<ProviderName, string> = {
  gmail: "Google Gmail",
  outlook: "Microsoft Outlook",
};

function ProviderRow({ provider, connected, updatedAt }: { provider: ProviderName; connected: boolean; updatedAt: string | null }) {
  const queryClient = useQueryClient();
  const [feedback, setFeedback] = useState<string | null>(null);

  const connectMutation = useMutation({
    mutationFn: () => getProviderLoginUrl(provider),
    onSuccess: ({ auth_url }) => {
      window.location.href = auth_url;
    },
    onError: () => setFeedback("Impossible de générer l'URL de connexion."),
  });

  const disconnectMutation = useMutation({
    mutationFn: () => disconnectProvider(provider),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "status"] });
      setFeedback(`${PROVIDER_LABELS[provider]} déconnecté.`);
    },
    onError: () => setFeedback("Erreur lors de la déconnexion."),
  });

  const isPending = connectMutation.isPending || disconnectMutation.isPending;

  return (
    <Card className="space-y-3">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="font-semibold text-slate-900">{PROVIDER_LABELS[provider]}</p>
          {connected && updatedAt && (
            <p className="text-xs text-slate-500">
              Connecté le {new Date(updatedAt).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}
            </p>
          )}
        </div>
        <Badge variant={connected ? "success" : "warning"}>
          {connected ? "Connecté" : "Non connecté"}
        </Badge>
      </div>

      {feedback && <Alert variant={feedback.includes("Erreur") || feedback.includes("Impossible") ? "error" : "success"}>{feedback}</Alert>}

      <div className="flex gap-2">
        <Button isLoading={connectMutation.isPending} disabled={isPending} onClick={() => connectMutation.mutate()}>
          {connected ? "Reconnecter" : "Se connecter"}
        </Button>
        {connected && (
          <Button
            variant="danger"
            isLoading={disconnectMutation.isPending}
            disabled={isPending}
            onClick={() => disconnectMutation.mutate()}
          >
            Déconnecter
          </Button>
        )}
      </div>
    </Card>
  );
}

export function SettingsPage() {
  const { data, isLoading } = useAuthStatus();

  const providers = data?.providers ?? [
    { provider: "gmail" as ProviderName, connected: false, updated_at: null },
    { provider: "outlook" as ProviderName, connected: false, updated_at: null },
  ];

  return (
    <main className="space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Paramètres</h1>
        <p className="mt-1 text-sm text-slate-500">Gère les connexions aux providers de messagerie.</p>
      </div>

      <section className="space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Providers connectés</h2>
        {isLoading ? (
          <p className="text-sm text-slate-500">Chargement...</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {providers.map((p) => (
              <ProviderRow
                key={p.provider}
                provider={p.provider}
                connected={p.connected}
                updatedAt={p.updated_at}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

