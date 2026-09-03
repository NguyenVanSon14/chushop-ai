import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createManualSalesOrder,
  type ManualSalesOrderInput,
  createSalesImport,
  deleteSalesOrder,
  listSalesOrders,
  previewSalesImport,
} from "./api";

const salesKey = (businessId: string) => ["sales-orders", businessId] as const;

export function useSalesOrders(businessId?: string) {
  return useQuery({
    queryKey: salesKey(businessId ?? ""),
    queryFn: () => listSalesOrders(businessId!),
    enabled: Boolean(businessId),
  });
}

export function usePreviewSales(businessId: string) {
  return useMutation({ mutationFn: (file: File) => previewSalesImport(businessId, file) });
}

export function useImportSales(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => createSalesImport(businessId, file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: salesKey(businessId) }),
  });
}

export function useCreateManualSalesOrder(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ManualSalesOrderInput) => createManualSalesOrder(businessId, input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: salesKey(businessId) }),
  });
}

export function useDeleteSalesOrder(businessId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orderId: string) => deleteSalesOrder(businessId, orderId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: salesKey(businessId) }),
  });
}
