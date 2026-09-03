"use client";

import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api/client";
import type { Product } from "@/lib/api/types";
import type { ProductInput } from "./api";
import { useCreateProduct, useUpdateProduct } from "./hooks";
import { productSchema } from "./schema";

export function ProductForm({
  businessId,
  product,
  onDone,
}: {
  businessId: string;
  product: Product | null;
  onDone: () => void;
}) {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const createMutation = useCreateProduct(businessId);
  const updateMutation = useUpdateProduct(businessId);
  const mutation = product ? updateMutation : createMutation;

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const parsed = productSchema.safeParse({
      name: data.get("name"),
      sku: data.get("sku"),
      selling_price: data.get("selling_price"),
      cost_price: data.get("cost_price"),
      is_active: data.get("is_active") === "on",
    });
    if (!parsed.success) {
      setErrors(
        Object.fromEntries(parsed.error.issues.map((issue) => [issue.path[0], issue.message])),
      );
      return;
    }
    setErrors({});
    const input: ProductInput = { ...parsed.data, sku: parsed.data.sku || null };
    const options = { onSuccess: () => { form.reset(); onDone(); } };
    if (product) updateMutation.mutate({ productId: product.id, input }, options);
    else createMutation.mutate(input, options);
  }

  const serverError = mutation.error instanceof ApiError ? mutation.error.message : null;
  return (
    <form onSubmit={submit} className="space-y-5" noValidate>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Tên sản phẩm" error={errors.name} className="sm:col-span-2">
          <Input name="name" defaultValue={product?.name} placeholder="Ví dụ: Áo thun basic" />
        </Field>
        <Field label="SKU" error={errors.sku}>
          <Input name="sku" defaultValue={product?.sku ?? ""} placeholder="SP-001" />
        </Field>
        <label className="flex items-center gap-3 self-end pb-3 text-sm font-semibold">
          <input name="is_active" type="checkbox" defaultChecked={product?.is_active ?? true} className="size-4 accent-green-700" />
          Đang kinh doanh
        </label>
        <Field label="Giá bán (VND)" error={errors.selling_price}>
          <Input name="selling_price" type="number" min="0" step="1" defaultValue={product?.selling_price ?? ""} />
        </Field>
        <Field label="Giá vốn (VND)" error={errors.cost_price}>
          <Input name="cost_price" type="number" min="0" step="1" defaultValue={product?.cost_price ?? ""} />
        </Field>
      </div>
      {serverError && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{serverError}</p>}
      <div className="flex flex-wrap gap-3">
        <Button disabled={mutation.isPending}>{mutation.isPending ? "Đang lưu..." : product ? "Lưu thay đổi" : "Thêm sản phẩm"}</Button>
        {product && <Button type="button" onClick={onDone} className="bg-white text-green-800 ring-1 ring-green-800 hover:bg-green-50">Hủy</Button>}
      </div>
    </form>
  );
}

function Field({ label, error, className = "", children }: { label: string; error?: string; className?: string; children: React.ReactNode }) {
  return <label className={`block space-y-2 ${className}`}><span className="text-sm font-semibold">{label}</span>{children}{error && <span className="block text-sm text-red-600">{error}</span>}</label>;
}
