"use client";

import Link from "next/link";
import { type FormEvent, useState } from "react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useProducts } from "@/features/products/hooks";
import { ApiError } from "@/lib/api/client";
import { useCreateManualSalesOrder } from "./hooks";

const itemSchema = z.object({
  product_id: z.string().uuid("Hãy chọn sản phẩm"),
  quantity: z.coerce.number().int("Số lượng phải là số nguyên").positive("Số lượng phải lớn hơn 0"),
  unit_price: z.coerce.number().int("Đơn giá phải là số nguyên").nonnegative("Đơn giá không được âm"),
});

const orderSchema = z.object({
  order_code: z.string().trim().max(100).transform((value) => value || null),
  channel: z.string().trim().min(1, "Hãy nhập kênh bán").max(50),
  ordered_at: z.string().min(1, "Hãy chọn thời gian bán"),
  fees: z.coerce.number().int("Phí phải là số nguyên").nonnegative("Phí không được âm"),
  items: z.array(itemSchema).min(1).max(50),
});

type DraftItem = {
  key: number;
  product_id: string;
  quantity: string;
  unit_price: string;
};

const emptyItem = (key: number): DraftItem => ({
  key,
  product_id: "",
  quantity: "1",
  unit_price: "",
});

function localDateTime() {
  const date = new Date();
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
  return date.toISOString().slice(0, 16);
}

export function ManualSalesForm({ businessId }: { businessId: string }) {
  const products = useProducts(businessId);
  const createOrder = useCreateManualSalesOrder(businessId);
  const [items, setItems] = useState<DraftItem[]>([emptyItem(1)]);
  const [nextKey, setNextKey] = useState(2);
  const [formKey, setFormKey] = useState(1);
  const [error, setError] = useState("");

  function updateItem(key: number, changes: Partial<DraftItem>) {
    setItems((current) => current.map((item) => item.key === key ? { ...item, ...changes } : item));
  }

  function selectProduct(item: DraftItem, productId: string) {
    const product = products.data?.find((candidate) => candidate.id === productId);
    updateItem(item.key, {
      product_id: productId,
      unit_price: product ? String(product.selling_price) : "",
    });
  }

  function addItem() {
    setItems((current) => [...current, emptyItem(nextKey)]);
    setNextKey((value) => value + 1);
  }

  function removeItem(key: number) {
    setItems((current) => current.filter((item) => item.key !== key));
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const parsed = orderSchema.safeParse({
      order_code: form.get("order_code"),
      channel: form.get("channel"),
      ordered_at: form.get("ordered_at"),
      fees: form.get("fees"),
      items,
    });
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? "Dữ liệu chưa hợp lệ");
      return;
    }
    createOrder.mutate(parsed.data, {
      onSuccess: () => {
        setItems([emptyItem(nextKey)]);
        setNextKey((value) => value + 1);
        setFormKey((value) => value + 1);
      },
    });
  }

  if (products.isLoading) return <p className="py-8 text-center text-[var(--muted)]">Đang tải sản phẩm...</p>;
  if (!products.data?.length) {
    return <div className="rounded-2xl bg-amber-50 p-5 text-sm text-amber-900"><p className="font-bold">Bạn chưa có sản phẩm để bán.</p><p className="mt-1">Tạo sản phẩm trước để hệ thống tự chụp giá vốn lịch sử.</p><Link className="mt-3 inline-flex font-bold underline" href="/products">Đi đến Sản phẩm →</Link></div>;
  }

  const serverError = createOrder.error instanceof ApiError ? createOrder.error.message : null;
  return (
    <form key={formKey} className="space-y-6" onSubmit={submit} noValidate>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Field label="Mã đơn (không bắt buộc)"><Input name="order_code" placeholder="Tự tạo nếu để trống" /></Field>
        <Field label="Kênh bán"><Input name="channel" defaultValue="CỬA HÀNG" placeholder="Cửa hàng, Shopee..." /></Field>
        <Field label="Thời gian bán"><Input name="ordered_at" type="datetime-local" defaultValue={localDateTime()} /></Field>
        <Field label="Phí bán hàng (VND)"><Input name="fees" type="number" min="0" step="1" defaultValue="0" /></Field>
      </div>

      <div>
        <div className="mb-3 flex items-center justify-between"><div><h3 className="font-bold">Sản phẩm trong đơn</h3><p className="text-sm text-[var(--muted)]">Giá vốn được backend tự động lưu tại thời điểm tạo đơn.</p></div><Button className="h-9 bg-white px-3 text-emerald-800 ring-1 ring-emerald-700/30 hover:bg-emerald-50" onClick={addItem} type="button">+ Thêm dòng</Button></div>
        <div className="space-y-3">
          {items.map((item, index) => (
            <div key={item.key} className="grid gap-3 rounded-2xl border border-[var(--border)] bg-slate-50/60 p-4 md:grid-cols-[minmax(0,1fr)_120px_180px_auto] md:items-end">
              <Field label={`Sản phẩm ${index + 1}`}><select className="h-11 w-full rounded-xl border border-[var(--border)] bg-white px-3 outline-none focus:border-emerald-600" value={item.product_id} onChange={(event) => selectProduct(item, event.target.value)}><option value="">Chọn sản phẩm</option>{products.data.filter((product) => product.is_active).map((product) => <option key={product.id} value={product.id}>{product.name} {product.sku ? `· ${product.sku}` : ""}</option>)}</select></Field>
              <Field label="Số lượng"><Input min="1" step="1" type="number" value={item.quantity} onChange={(event) => updateItem(item.key, { quantity: event.target.value })} /></Field>
              <Field label="Đơn giá thực bán"><Input min="0" step="1" type="number" value={item.unit_price} onChange={(event) => updateItem(item.key, { unit_price: event.target.value })} /></Field>
              <Button aria-label={`Xóa sản phẩm ${index + 1}`} className="h-11 bg-white px-3 text-red-700 ring-1 ring-red-200 hover:bg-red-50" disabled={items.length === 1} onClick={() => removeItem(item.key)} type="button">Xóa</Button>
            </div>
          ))}
        </div>
      </div>

      {(error || serverError) && <p className="rounded-xl bg-red-50 p-3 text-sm font-semibold text-red-700" role="alert">{error || serverError}</p>}
      {createOrder.isSuccess && <p className="rounded-xl bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">Đã ghi nhận đơn bán hàng.</p>}
      <Button disabled={createOrder.isPending}>{createOrder.isPending ? "Đang ghi nhận..." : "Ghi nhận đơn hàng"}</Button>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block space-y-2"><span className="text-sm font-semibold">{label}</span>{children}</label>;
}
