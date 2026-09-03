import { apiRequest } from "@/lib/api/client";
import type { Product } from "@/lib/api/types";

export type ProductInput = {
  name: string;
  sku?: string | null;
  selling_price: number;
  cost_price: number;
  is_active: boolean;
};

const path = (businessId: string) => `/businesses/${businessId}/products`;

export const listProducts = (businessId: string) => apiRequest<Product[]>(path(businessId));

export const createProduct = (businessId: string, input: ProductInput) =>
  apiRequest<Product>(path(businessId), { method: "POST", body: JSON.stringify(input) });

export const updateProduct = (
  businessId: string,
  productId: string,
  input: ProductInput,
) =>
  apiRequest<Product>(`${path(businessId)}/${productId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });

export const deleteProduct = (businessId: string, productId: string) =>
  apiRequest<void>(`${path(businessId)}/${productId}`, { method: "DELETE" });
