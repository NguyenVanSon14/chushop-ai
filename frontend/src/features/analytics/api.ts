import { apiRequest } from "@/lib/api/client";
import type { Analytics } from "@/lib/api/types";

export function getAnalytics(businessId: string, dateFrom: string, dateTo: string) {
  const query = new URLSearchParams({ date_from: dateFrom, date_to: dateTo });
  return apiRequest<Analytics>(`/businesses/${businessId}/analytics/summary?${query}`);
}
