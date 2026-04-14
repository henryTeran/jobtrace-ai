import { createBrowserRouter, Navigate } from "react-router-dom";

import { AuthConnectPage } from "../../modules/auth/pages/AuthConnectPage";
import { AuthStatusPage } from "../../modules/auth/pages/AuthStatusPage";
import { DashboardPage } from "../../modules/dashboard/pages/DashboardPage";
import { EmailsPage } from "../../modules/emails/pages/EmailsPage";
import { ReportsPage } from "../../modules/reports/pages/ReportsPage";
import { SettingsPage } from "../../modules/settings/pages/SettingsPage";
import { SyncPage } from "../../modules/sync/pages/SyncPage";
import { RequireConnectedGuard } from "../guards/RequireConnectedGuard";
import { RedirectIfConnectedGuard } from "../guards/RedirectIfConnectedGuard";
import { AppLayout } from "../layout/AppLayout";

export const appRouter = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/dashboard" replace />,
  },
  {
    element: <RedirectIfConnectedGuard />,
    children: [
      { path: "/auth/connect", element: <AuthConnectPage /> },
    ],
  },
  {
    path: "/auth/status",
    element: <AuthStatusPage />,
  },
  {
    element: <RequireConnectedGuard />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: "/dashboard", element: <DashboardPage /> },
          { path: "/sync", element: <SyncPage /> },
          { path: "/emails", element: <EmailsPage /> },
          { path: "/reports", element: <ReportsPage /> },
          { path: "/settings", element: <SettingsPage /> },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/dashboard" replace />,
  },
]);
