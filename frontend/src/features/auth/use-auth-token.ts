"use client";

import { useSyncExternalStore } from "react";
import { getAccessToken, subscribeToToken } from "@/lib/auth/token-storage";

export function useHasAccessToken(): boolean {
  return useSyncExternalStore(
    subscribeToToken,
    () => getAccessToken() !== null,
    () => false,
  );
}
