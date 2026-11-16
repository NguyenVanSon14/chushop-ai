import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listAdminAuditLogs,
  listAdminBusinesses,
  listAdminUsers,
  updateAdminUserStatus,
} from "./api";

export const useAdminUsers = (enabled: boolean) =>
  useQuery({ queryKey: ["admin", "users"], queryFn: listAdminUsers, enabled });

export const useAdminBusinesses = (enabled: boolean) =>
  useQuery({
    queryKey: ["admin", "businesses"],
    queryFn: listAdminBusinesses,
    enabled,
  });

export const useAdminAuditLogs = (enabled: boolean) =>
  useQuery({
    queryKey: ["admin", "audit-logs"],
    queryFn: listAdminAuditLogs,
    enabled,
  });

export function useUpdateAdminUserStatus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateAdminUserStatus,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      void queryClient.invalidateQueries({ queryKey: ["admin", "audit-logs"] });
    },
  });
}
