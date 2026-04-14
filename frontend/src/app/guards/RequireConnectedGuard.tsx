import { Navigate, Outlet } from "react-router-dom";

import { useAuthStatus } from "../../modules/auth/hooks/useAuthStatus";
import { Loader } from "../../shared/ui";

export function RequireConnectedGuard() {
  const { isLoading, summary } = useAuthStatus();

  if (isLoading) {
    return (
      <div className="p-6">
        <Loader />
      </div>
    );
  }

  if (!summary.isConnected) {
    return <Navigate to="/auth/connect" replace />;
  }

  return <Outlet />;
}
