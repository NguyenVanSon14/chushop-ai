import { apiRequest } from "@/lib/api/client";
import type { ImportPreview, SalesImport, SalesOrder } from "@/lib/api/types";

const basePath = (businessId: string) => `/businesses/${businessId}/sales`;

function fileBody(file: File): FormData {
  const body = new FormData();
  body.append("file", file);
  return body;
}

export const previewSalesImport = (businessId: string, file: File) =>
  apiRequest<ImportPreview>(`${basePath(businessId)}/imports/preview`, {
    method: "POST",
    body: fileBody(file),
  });

export const createSalesImport = (businessId: string, file: File) =>
  apiRequest<SalesImport>(`${basePath(businessId)}/imports`, {
    method: "POST",
    body: fileBody(file),
  });

export const listSalesOrders = (businessId: string) =>
  apiRequest<SalesOrder[]>(`${basePath(businessId)}/orders`);

export type ManualSalesOrderInput = {
  order_code: string | null;
  channel: string;
  ordered_at: string;
  fees: number;
  items: Array<{
    product_id: string;
    quantity: number;
    unit_price: number;
  }>;
};

export const createManualSalesOrder = (
  businessId: string,
  input: ManualSalesOrderInput,
) =>
  apiRequest<SalesOrder>(`${basePath(businessId)}/orders`, {
    method: "POST",
    body: JSON.stringify(input),
  });

export const deleteSalesOrder = (businessId: string, orderId: string) =>
  apiRequest<void>(`${basePath(businessId)}/orders/${orderId}`, {
    method: "DELETE",
  });

export const deleteSalesImport = (businessId: string, importId: string) =>
  apiRequest<void>(`${basePath(businessId)}/imports/${importId}`, {
    method: "DELETE",
  });
