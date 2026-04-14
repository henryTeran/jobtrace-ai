import type { ReactNode } from "react";

import { Button } from "./Button";
import { Card } from "./Card";

type EmptyStateProps = {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: ReactNode;
};

export function EmptyState({ title, description, actionLabel, onAction, icon }: EmptyStateProps) {
  return (
    <Card className="flex flex-col items-start gap-4 border-dashed">
      {icon ? <div className="text-slate-500">{icon}</div> : null}
      <div>
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <p className="mt-1 text-sm text-slate-600">{description}</p>
      </div>
      {actionLabel && onAction ? <Button onClick={onAction}>{actionLabel}</Button> : null}
    </Card>
  );
}
