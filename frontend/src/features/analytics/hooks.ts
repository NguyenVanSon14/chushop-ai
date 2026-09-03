import { useQuery } from "@tanstack/react-query";
import { getAnalytics } from "./api";

export function useAnalytics(businessId: string | undefined, dateFrom: string, dateTo: string) {
  return useQuery({
    queryKey: ["analytics", businessId, dateFrom, dateTo],
    queryFn: () => getAnalytics(businessId!, dateFrom, dateTo),
    enabled: Boolean(businessId && dateFrom && dateTo),
  });
}
