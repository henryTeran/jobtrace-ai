import type { PropsWithChildren } from "react";

import { cn } from "../lib/cn";

type BadgeVariant = "success" | "warning" | "danger" | "neutral";

type BadgeProps = PropsWithChildren<{
  variant?: BadgeVariant;
  className?: string;
}>;

const variantClasses: Record<BadgeVariant, string> = {
  success: "bg-emerald-100 text-emerald-800",
  warning: "bg-amber-100 text-amber-800",
  danger: "bg-rose-100 text-rose-800",
  neutral: "bg-slate-100 text-slate-700",
};

export function Badge({ variant = "neutral", className, children }: BadgeProps) {
  return (
    <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold", variantClasses[variant], className)}>
      {children}
    </span>
  );
}
