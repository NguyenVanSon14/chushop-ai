import { apiRequest } from "@/lib/api/client";
import type { AdminAuditLog, AdminBusiness, AdminUser } from "@/lib/api/types";

export const listAdminUsers = () => apiRequest<AdminUser[]>("/admin/users");
export const listAdminBusinesses = () =>
  apiRequest<AdminBusiness[]>("/admin/businesses");
export const listAdminAuditLogs = () =>
  apiRequest<AdminAuditLog[]>("/admin/audit-logs");

export const updateAdminUserStatus = ({
  userId,
  isActive,
}: {
  userId: string;
  isActive: boolean;
}) =>
  apiRequest<AdminUser>(`/admin/users/${userId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ is_active: isActive }),
  });
