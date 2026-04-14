import { Navigate, Outlet } from "react-router-dom";

import { useAuthStatus } from "../../modules/auth/hooks/useAuthStatus";
import { Loader } from "../../shared/ui";

export function RedirectIfConnectedGuard() {
  const { isLoading, summary } = useAuthStatus();

  if (isLoading) {
    return (
      <div className="p-6">
        <Loader />
      </div>
    );
  }

  if (summary.isConnected) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
