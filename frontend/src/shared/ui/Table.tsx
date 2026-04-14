import type { PropsWithChildren, TableHTMLAttributes } from "react";

import { cn } from "../lib/cn";

export function Table({ className, children, ...props }: PropsWithChildren<TableHTMLAttributes<HTMLTableElement>>) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className={cn("min-w-full border-collapse text-left text-sm", className)} {...props}>
        {children}
      </table>
    </div>
  );
}
