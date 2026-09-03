import { z } from "zod";

export const productSchema = z.object({
  name: z.string().trim().min(1, "Vui lòng nhập tên sản phẩm").max(255),
  sku: z.string().trim().max(100, "SKU tối đa 100 ký tự").optional(),
  selling_price: z.coerce.number().int("Giá bán phải là số nguyên").min(0, "Giá bán không được âm"),
  cost_price: z.coerce.number().int("Giá vốn phải là số nguyên").min(0, "Giá vốn không được âm"),
  is_active: z.boolean(),
});
