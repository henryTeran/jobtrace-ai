import { useMutation } from "@tanstack/react-query";

import { mapAxiosError } from "../../../shared/api/errors";
import { Alert, Badge, Button, Card } from "../../../shared/ui";
import { getProviderLoginUrl } from "../api/auth.api";
import type { ProviderName } from "../types/auth.types";

type ProviderCardProps = {
  provider: ProviderName;
  connected: boolean;
};

const providerLabel: Record<ProviderName, string> = {
  gmail: "Google",
  outlook: "Microsoft",
};

export function ProviderCard({ provider, connected }: ProviderCardProps) {
  const loginMutation = useMutation({
    mutationFn: () => getProviderLoginUrl(provider),
    onSuccess: ({ auth_url }) => {
      window.location.href = auth_url;
    },
  });

  const mappedError = loginMutation.error ? mapAxiosError(loginMutation.error) : null;

  return (
    <Card className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">{providerLabel[provider]}</h3>
        <Badge variant={connected ? "success" : "warning"}>{connected ? "Connecté" : "Non connecté"}</Badge>
      </div>
      {mappedError ? <Alert variant="error">{mappedError.message}</Alert> : null}
      <Button isLoading={loginMutation.isPending} onClick={() => loginMutation.mutate()}>
        {connected ? "Reconnecter" : "Se connecter"}
      </Button>
    </Card>
  );
}
