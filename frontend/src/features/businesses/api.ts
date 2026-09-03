import { apiRequest } from "@/lib/api/client";
import type { Business } from "@/lib/api/types";

export const listBusinesses = () => apiRequest<Business[]>("/businesses");
export const createBusiness = (name: string) =>
  apiRequest<Business>("/businesses", { method: "POST", body: JSON.stringify({ name }) });
