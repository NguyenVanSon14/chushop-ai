import * as React from "react";
import { cn } from "@/lib/utils";

export function Button({ className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "inline-flex h-11 items-center justify-center rounded-xl bg-[var(--brand)] px-5 font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-[var(--brand-dark)] hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0",
        className,
      )}
      {...props}
    />
  );
}
