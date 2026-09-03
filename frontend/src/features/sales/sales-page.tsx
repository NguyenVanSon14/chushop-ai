"use client";

import { useRouter } from "next/navigation";
import { type ChangeEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useHasAccessToken } from "@/features/auth/use-auth-token";
import { useActiveBusiness, useBusinesses } from "@/features/businesses/hooks";
import { ApiError } from "@/lib/api/client";
import { useDeleteSalesOrder, useImportSales, usePreviewSales, useSalesOrders } from "./hooks";
import { ManualSalesForm } from "./manual-sales-form";

const money = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
});

export function SalesPage() {
  const router = useRouter();
  const authenticated = useHasAccessToken();
  const businesses = useBusinesses(authenticated);
  const business = useActiveBusiness(businesses.data);
  const orders = useSalesOrders(business?.id);
  const previewMutation = usePreviewSales(business?.id ?? "");
  const importMutation = useImportSales(business?.id ?? "");
  const deleteMutation = useDeleteSalesOrder(business?.id ?? "");
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<"manual" | "file">("manual");

  useEffect(() => {
    if (!authenticated) router.replace("/login");
  }, [authenticated, router]);

  function selectFile(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
    previewMutation.reset();
    importMutation.reset();
  }

  function commit() {
    if (!file) return;
    importMutation.mutate(file, {
      onSuccess: () => {
        setFile(null);
        previewMutation.reset();
      },
    });
  }

  if (!authenticated || businesses.isLoading) return <Status text="Đang tải doanh nghiệp..." />;
  if (!business) return <Status text="Bạn cần tạo doanh nghiệp trước." />;
  const preview = previewMutation.data;

  return (
    <AppShell businessId={business.id} businessName={business.name} businesses={businesses.data ?? []}>
      <div>
        <p className="text-xs font-extrabold uppercase tracking-[0.18em] text-emerald-700">Dữ liệu tiền</p>
        <h1 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">Bán hàng</h1>
        <p className="mt-3 max-w-2xl text-[var(--muted)]">Ghi từng đơn ngay trên hệ thống hoặc tải file khi bạn có nhiều dữ liệu.</p>

        <div className="mt-7 inline-flex rounded-2xl border border-[var(--border)] bg-white p-1.5 shadow-sm" role="tablist">
          <ModeButton active={mode === "manual"} onClick={() => setMode("manual")}>✍ Nhập thủ công</ModeButton>
          <ModeButton active={mode === "file"} onClick={() => setMode("file")}>↑ Tải file CSV/XLSX</ModeButton>
        </div>

        {mode === "manual" ? (
          <Card className="mt-5 p-5 sm:p-7"><div className="mb-6"><h2 className="text-xl font-bold">Tạo đơn bán hàng</h2><p className="mt-1 text-sm text-[var(--muted)]">Phù hợp khi shop không xuất được file hoặc chỉ cần nhập vài đơn mỗi ngày.</p></div><ManualSalesForm key={business.id} businessId={business.id} /></Card>
        ) : (
          <>
            <FileImportCard
              file={file}
              importMutation={importMutation}
              previewMutation={previewMutation}
              onCommit={commit}
              onSelect={selectFile}
            />
            {preview && <PreviewCard preview={preview} pending={importMutation.isPending} onCommit={commit} />}
          </>
        )}

        <section className="mt-9">
          <div className="mb-4 flex items-end justify-between"><div><h2 className="text-xl font-bold">Lịch sử đơn hàng</h2><p className="mt-1 text-sm text-[var(--muted)]">Cả đơn nhập thủ công và đơn từ file đều xuất hiện tại đây.</p></div><span className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-[var(--muted)] shadow-sm">{orders.data?.length ?? 0} đơn</span></div>
          {orders.isLoading && <Card className="p-10 text-center text-[var(--muted)]">Đang tải đơn hàng...</Card>}
          {orders.isError && <Card className="p-10 text-center text-red-700">Không thể tải đơn hàng.</Card>}
          {orders.data?.length === 0 && <Card className="p-10 text-center"><p className="font-bold">Chưa có đơn bán hàng</p><p className="mt-2 text-sm text-[var(--muted)]">Nhập thủ công đơn đầu tiên bằng biểu mẫu phía trên.</p></Card>}
          <div className="grid gap-3">
            {orders.data?.map((order) => {
              const isShopee = order.channel.toUpperCase() === "SHOPEE";
              const isTikTok = order.channel.toUpperCase() === "TIKTOK";
              return (
                <Card key={order.id} className="grid gap-4 p-5 transition hover:border-emerald-200 hover:shadow-md sm:grid-cols-[1fr_auto] sm:items-center">
                  <div className="flex items-center gap-3">
                    <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-emerald-50 font-bold text-emerald-700">₫</span>
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-bold">{order.external_id}</h3>
                        <span className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${isShopee ? "bg-orange-100 text-orange-800" : isTikTok ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600"}`}>
                          {order.channel}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-[var(--muted)]">{new Date(order.ordered_at).toLocaleString("vi-VN")} · {order.items.length} sản phẩm</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 sm:gap-6">
                    <div className="grid grid-cols-2 gap-6 text-sm sm:text-right">
                      <div><p className="text-[var(--muted)]">Doanh thu</p><p className="mt-1 font-extrabold text-emerald-800">{money.format(order.revenue)}</p></div>
                      <div><p className="text-[var(--muted)]">Phí</p><p className="mt-1 font-bold text-red-700">{money.format(order.fees)}</p></div>
                    </div>
                    <button aria-label={`Xóa đơn ${order.external_id}`} className="grid size-9 shrink-0 place-items-center rounded-xl text-slate-400 transition hover:bg-red-50 hover:text-red-600" disabled={deleteMutation.isPending} onClick={() => { if (confirm(`Bạn muốn xóa đơn ${order.external_id}?`)) deleteMutation.mutate(order.id); }} type="button">✕</button>
                  </div>
                </Card>
              );
            })}
          </div>
        </section>
      </div>
    </AppShell>
  );
}

function FileImportCard({ file, importMutation, previewMutation, onCommit, onSelect }: { file: File | null; importMutation: ReturnType<typeof useImportSales>; previewMutation: ReturnType<typeof usePreviewSales>; onCommit: () => void; onSelect: (event: ChangeEvent<HTMLInputElement>) => void }) {
  return <Card className="mt-5 p-5 sm:p-7"><div className="flex size-12 items-center justify-center rounded-2xl bg-emerald-50 text-xl text-emerald-800">↑</div><h2 className="mt-4 text-xl font-bold">Nhập CSV hoặc XLSX</h2><p className="mt-2 text-sm text-[var(--muted)]">Cần các cột: order_code, channel, ordered_at, sku, quantity, unit_price, fees.</p><div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center"><input key={file?.name ?? "empty"} className="block w-full rounded-xl border border-dashed border-emerald-300 bg-emerald-50/40 p-3 text-sm" type="file" accept=".csv,.xlsx" onChange={onSelect} /><Button className="shrink-0" disabled={!file || previewMutation.isPending} onClick={() => file && previewMutation.mutate(file)}>{previewMutation.isPending ? "Đang kiểm tra..." : "Xem trước"}</Button></div>{previewMutation.isError && <ErrorMessage error={previewMutation.error} />}{importMutation.isError && <ErrorMessage error={importMutation.error} />}{importMutation.isSuccess && <p className="mt-4 rounded-xl bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">Nhập dữ liệu thành công.</p>}<button className="sr-only" onClick={onCommit} type="button">Xác nhận nhập</button></Card>;
}

function PreviewCard({ preview, pending, onCommit }: { preview: NonNullable<ReturnType<typeof usePreviewSales>["data"]>; pending: boolean; onCommit: () => void }) {
  return <Card className="mt-5 p-5 sm:p-7"><div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><h2 className="text-xl font-bold">Kết quả xem trước</h2><p className="mt-1 text-sm text-[var(--muted)]">{preview.order_count} đơn · {preview.row_count} dòng</p></div><Button disabled={pending} onClick={onCommit}>{pending ? "Đang nhập..." : "Xác nhận nhập"}</Button></div><div className="mt-5 grid gap-3 sm:grid-cols-3"><Metric label="Doanh thu" value={preview.total_revenue} /><Metric label="Giá vốn snapshot" value={preview.total_cost} /><Metric label="Phí" value={preview.total_fees} /></div><div className="mt-5 overflow-x-auto"><table className="w-full min-w-[650px] text-left text-sm"><thead className="border-b text-[var(--muted)]"><tr><th className="p-3">Đơn</th><th className="p-3">Kênh</th><th className="p-3">SKU</th><th className="p-3 text-right">SL</th><th className="p-3 text-right">Đơn giá</th><th className="p-3 text-right">Giá vốn</th></tr></thead><tbody>{preview.rows.map((row, index) => <tr key={`${row.order_code}-${row.sku}-${index}`} className="border-b last:border-0"><td className="p-3 font-semibold">{row.order_code}</td><td className="p-3">{row.channel}</td><td className="p-3">{row.sku}</td><td className="p-3 text-right">{row.quantity}</td><td className="p-3 text-right">{money.format(row.unit_price)}</td><td className="p-3 text-right">{money.format(row.cost_price_snapshot)}</td></tr>)}</tbody></table></div></Card>;
}

function ModeButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return <button className={`rounded-xl px-4 py-2.5 text-sm font-bold transition ${active ? "bg-emerald-800 text-white shadow-sm" : "text-[var(--muted)] hover:bg-emerald-50 hover:text-emerald-800"}`} onClick={onClick} role="tab" aria-selected={active} type="button">{children}</button>;
}

function Metric({ label, value }: { label: string; value: number }) {
  return <div className="rounded-xl bg-slate-50 p-4"><p className="text-sm text-[var(--muted)]">{label}</p><p className="mt-1 font-extrabold">{money.format(value)}</p></div>;
}

function Status({ text }: { text: string }) {
  return <main className="flex min-h-screen items-center justify-center p-6 text-[var(--muted)]">{text}</main>;
}

function ErrorMessage({ error }: { error: Error }) {
  return <p className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error instanceof ApiError ? error.message : "Không thể xử lý tệp"}</p>;
}
