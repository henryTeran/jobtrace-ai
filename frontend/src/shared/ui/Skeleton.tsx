import { cn } from "../lib/cn";

type SkeletonProps = {
  className?: string;
};

export function Skeleton({ className }: SkeletonProps) {
  return <div className={cn("animate-pulse rounded-md bg-slate-200", className)} aria-hidden="true" />;
}
