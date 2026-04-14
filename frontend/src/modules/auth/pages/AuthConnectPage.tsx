import { ProviderCard } from "../components/ProviderCard";
import { useAuthStatus } from "../hooks/useAuthStatus";

export function AuthConnectPage() {
  const { data } = useAuthStatus();

  const providers = data?.providers ?? [
    { provider: "gmail" as const, connected: false, updated_at: null },
    { provider: "outlook" as const, connected: false, updated_at: null },
  ];

  return (
    <main className="mx-auto w-full max-w-5xl px-6 py-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Connexion des providers</h1>
        <p className="mt-2 text-sm text-slate-600">Connecte au moins un provider pour activer la synchronisation.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {providers.map((provider) => (
          <ProviderCard key={provider.provider} provider={provider.provider} connected={provider.connected} />
        ))}
      </div>
    </main>
  );
}
