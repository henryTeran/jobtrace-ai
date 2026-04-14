import type { PropsWithChildren } from "react";

import { Button } from "./Button";
import { Card } from "./Card";

type ModalProps = PropsWithChildren<{
  isOpen: boolean;
  title: string;
  onClose: () => void;
}>;

export function Modal({ isOpen, title, onClose, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4">
      <Card className="w-full max-w-lg">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          <Button variant="ghost" onClick={onClose}>
            Fermer
          </Button>
        </div>
        {children}
      </Card>
    </div>
  );
}
