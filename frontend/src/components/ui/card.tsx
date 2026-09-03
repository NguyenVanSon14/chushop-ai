import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-2xl border border-[var(--border)] bg-white shadow-[0_1px_2px_rgba(15,40,27,.03),0_10px_30px_rgba(15,40,27,.04)]", className)} {...props} />;
}
