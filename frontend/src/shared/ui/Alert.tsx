import type { PropsWithChildren } from "react";

import { cn } from "../lib/cn";

type AlertVariant = "info" | "error" | "success";

type AlertProps = PropsWithChildren<{
  variant?: AlertVariant;
  className?: string;
}>;

const styles: Record<AlertVariant, string> = {
  info: "border-sky-200 bg-sky-50 text-sky-800",
  error: "border-rose-200 bg-rose-50 text-rose-800",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
};

export function Alert({ variant = "info", className, children }: AlertProps) {
  return <div className={cn("rounded-md border px-4 py-3 text-sm", styles[variant], className)}>{children}</div>;
}
