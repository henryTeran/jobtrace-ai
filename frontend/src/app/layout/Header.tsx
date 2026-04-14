import { Link } from "react-router-dom";

import { useAuthStatus } from "../../modules/auth/hooks/useAuthStatus";
import { Badge, Button } from "../../shared/ui";

export function Header() {
  const { summary } = useAuthStatus();

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-6 py-4">
      <div>
        <h1 className="text-lg font-semibold text-slate-900">SaaS Dashboard</h1>
        <p className="text-xs text-slate-500">Pilotage des connexions, sync, emails et rapports</p>
      </div>
      <div className="flex items-center gap-3">
        <Badge variant={summary.isConnected ? "success" : "warning"}>
          {summary.isConnected ? "Provider connecté" : "Aucun provider"}
        </Badge>
        <Link to="/sync">
          <Button variant="secondary">Sync Now</Button>
        </Link>
        <Button variant="ghost">Profil</Button>
      </div>
    </header>
  );
}
