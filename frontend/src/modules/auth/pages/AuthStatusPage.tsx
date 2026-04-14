import { Alert, Badge, Card, Loader } from "../../../shared/ui";
import { useAuthStatus } from "../hooks/useAuthStatus";

export function AuthStatusPage() {
  const { isLoading, data, mappedError } = useAuthStatus();

  if (isLoading) {
    return (
      <div className="p-6">
        <Loader />
      </div>
    );
  }

  if (mappedError) {
    return (
      <div className="p-6">
        <Alert variant="error">{mappedError.message}</Alert>
      </div>
    );
  }

  return (
    <main className="mx-auto w-full max-w-3xl px-6 py-10">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">Statut de connexion</h1>
      <div className="space-y-4">
        {data?.providers.map((provider) => (
          <Card key={provider.provider} className="flex items-center justify-between">
            <span className="font-medium text-slate-800">{provider.provider.toUpperCase()}</span>
            <Badge variant={provider.connected ? "success" : "warning"}>
              {provider.connected ? "Connecté" : "Non connecté"}
            </Badge>
          </Card>
        ))}
      </div>
    </main>
  );
}
