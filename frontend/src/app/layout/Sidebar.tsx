import { NavLink } from "react-router-dom";

import { cn } from "../../shared/lib/cn";
import { useAuthStatus } from "../../modules/auth/hooks/useAuthStatus";

const navigation = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/sync", label: "Sync" },
  { to: "/emails", label: "Emails" },
  { to: "/reports", label: "Reports" },
  { to: "/settings", label: "Settings" },
];

export function Sidebar() {
  const { data } = useAuthStatus();

  return (
    <aside className="w-full border-b border-slate-200 bg-white p-4 md:w-64 md:border-b-0 md:border-r">
      <div className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">JobTrace AI</div>
      <nav className="grid grid-cols-2 gap-2 md:grid-cols-1">
        {navigation.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "rounded-md px-3 py-2 text-sm font-medium transition",
                isActive ? "bg-teal-700 text-white" : "text-slate-700 hover:bg-slate-100",
              )
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {data && (
        <div className="mt-6 border-t border-slate-100 pt-4 space-y-1.5">
          {data.providers.map((p) => (
            <div key={p.provider} className="flex items-center gap-2 px-1">
              <span
                className={cn(
                  "h-2 w-2 rounded-full shrink-0",
                  p.connected ? "bg-emerald-500" : "bg-amber-400"
                )}
              />
              <span className="text-xs text-slate-500 capitalize">{p.provider}</span>
              <span className="ml-auto text-xs text-slate-400">
                {p.connected ? "connecté" : "—"}
              </span>
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}

