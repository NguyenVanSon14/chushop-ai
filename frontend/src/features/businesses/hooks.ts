"use client";

import { useSyncExternalStore } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import type { Business } from "@/lib/api/types";
import { createBusiness, listBusinesses } from "./api";

const ACTIVE_BUSINESS_KEY = "chushop_active_business_id";
const ACTIVE_BUSINESS_EVENT = "chushop-active-business-change";

function subscribe(callback: () => void) {
  window.addEventListener("storage", callback);
  window.addEventListener(ACTIVE_BUSINESS_EVENT, callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(ACTIVE_BUSINESS_EVENT, callback);
  };
}

function getSnapshot() {
  return window.localStorage.getItem(ACTIVE_BUSINESS_KEY) ?? "";
}

function getServerSnapshot() {
  return "";
}

export function selectActiveBusiness(businessId: string) {
  window.localStorage.setItem(ACTIVE_BUSINESS_KEY, businessId);
  window.dispatchEvent(new Event(ACTIVE_BUSINESS_EVENT));
}

export function useActiveBusiness(businesses?: Business[]) {
  const selectedId = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  return businesses?.find((business) => business.id === selectedId) ?? businesses?.[0];
}

export const useBusinesses = (enabled = true) =>
  useQuery({ queryKey: ["businesses"], queryFn: listBusinesses, enabled });
export const useCreateBusiness = () =>
  useMutation({
    mutationFn: createBusiness,
    onSuccess: (business) => selectActiveBusiness(business.id),
  });
