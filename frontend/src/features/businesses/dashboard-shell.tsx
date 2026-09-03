"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useAnalytics } from "@/features/analytics/hooks";
import { useHasAccessToken } from "@/features/auth/use-auth-token";
import type { Analytics, MetricComparison, TrendPoint } from "@/lib/api/types";
import { clearAccessToken } from "@/lib/auth/token-storage";
import { useActiveBusiness, useBusinesses } from "./hooks";

const money = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
});

function localDate(value: Date) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function initialPeriod() {
  const today = new Date();
  return {
    from: localDate(new Date(today.getFullYear(), today.getMonth(), 1)),
    to: localDate(today),
  };
}

export function DashboardShell() {
  const router = useRouter();
  const authenticated = useHasAccessToken();
  const businesses = useBusinesses(authenticated);
  const business = useActiveBusiness(businesses.data);
  const [period, setPeriod] = useState(initialPeriod);
  const analytics = useAnalytics(business?.id, period.from, period.to);

  useEffect(() => {
    if (!authenticated) router.replace("/login");
  }, [authenticated, router]);

  useEffect(() => {
    if (authenticated && businesses.data && businesses.data.length === 0) {
      router.replace("/onboarding/business");
    }
  }, [authenticated, businesses.data, router]);

  function logout() {
    clearAccessToken();
    router.replace("/login");
  }

  if (!authenticated || businesses.isLoading) {
    return <Status message="Đang tải bảng điều khiển..." />;
  }
  if (businesses.isError) {
    return <Status message="Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại." action={logout} />;
  }
  if (!business) return <Status message="Đang chuyển đến bước thiết lập..." />;

  return (
    <AppShell businessId={business.id} businessName={business.name} businesses={businesses.data ?? []}>
      <div>
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.16em] text-green-700">Money Brain</p>
            <h1 className="mt-2 text-3xl font-bold sm:text-4xl">Sức khỏe tài chính</h1>
            <p className="mt-2 text-[var(--muted)]">Doanh thu, chi phí và lợi nhuận được tính từ dữ liệu đã nhập.</p>
          </div>
          <div className="grid grid-cols-2 gap-3 rounded-2xl border border-[var(--border)] bg-white p-4">
            <DateField label="Từ ngày" value={period.from} onChange={(from) => setPeriod((old) => ({ ...old, from }))} />
            <DateField label="Đến ngày" value={period.to} onChange={(to) => setPeriod((old) => ({ ...old, to }))} />
          </div>
        </div>

        {analytics.isLoading && <Card className="mt-8 p-10 text-center text-[var(--muted)]">Đang tính báo cáo...</Card>}
        {analytics.isError && (
          <Card className="mt-8 p-8 text-center text-red-700">
            Không thể tải báo cáo. Hãy kiểm tra khoảng ngày và thử lại.
          </Card>
        )}
        {analytics.data && <DashboardContent analytics={analytics.data} />}
      </div>
    </AppShell>
  );
}

function DashboardContent({ analytics }: { analytics: Analytics }) {
  const { summary } = analytics;
  const empty = summary.order_count === 0 && summary.expenses === 0;
  if (empty) {
    return (
      <Card className="mt-8 p-8 text-center sm:p-12">
        <h2 className="text-xl font-bold">Chưa có dữ liệu trong khoảng này</h2>
        <p className="mt-2 text-[var(--muted)]">Nhập đơn bán hàng hoặc ghi nhận chi phí để Money Brain bắt đầu phân tích.</p>
        <div className="mt-5 flex justify-center gap-3">
          <Link className="rounded-xl bg-green-800 px-5 py-3 font-semibold text-white" href="/sales">Nhập bán hàng</Link>
          <Link className="rounded-xl bg-white px-5 py-3 font-semibold text-green-800 ring-1 ring-green-800" href="/expenses">Thêm chi phí</Link>
        </div>
      </Card>
    );
  }

  const lossProducts = analytics.products.filter((p) => p.gross_profit < 0);

  return (
    <>
      {lossProducts.length > 0 && (
        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-900 shadow-sm sm:flex sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-red-100 text-lg">⚠️</span>
            <div>
              <p className="font-bold">Cảnh báo Money Brain: {lossProducts.length} sản phẩm đang bán lỗ</p>
              <p className="mt-0.5 text-xs text-red-700">
                Sản phẩm {lossProducts[0].name} ({lossProducts[0].sku || "Không SKU"}) có lợi nhuận gộp âm {money.format(lossProducts[0].gross_profit)}.
              </p>
            </div>
          </div>
          <Link href="/products" className="mt-3 inline-block rounded-xl bg-red-700 px-4 py-2 text-xs font-bold text-white transition hover:bg-red-800 sm:mt-0">
            Xem sản phẩm
          </Link>
        </div>
      )}
      <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Doanh thu" value={summary.revenue} comparison={analytics.revenue_comparison} />
        <MetricCard label="Giá vốn" value={summary.cogs} />
        <MetricCard label="Lợi nhuận gộp" value={summary.gross_profit} margin={summary.gross_margin_bps} />
        <MetricCard label="Lợi nhuận ròng" value={summary.net_profit} margin={summary.net_margin_bps} comparison={analytics.net_profit_comparison} prominent />
        <MetricCard label="Phí bán hàng" value={summary.fees} />
        <MetricCard label="Chi phí vận hành" value={summary.expenses} />
        <Card className="p-5 sm:col-span-2">
          <p className="text-sm text-[var(--muted)]">Số đơn hàng</p>
          <p className="mt-2 text-3xl font-bold">{summary.order_count.toLocaleString("vi-VN")}</p>
          <p className="mt-2 text-sm text-[var(--muted)]">Trong kỳ báo cáo đã chọn</p>
        </Card>
      </section>
      <TrendChart points={analytics.trends} />
      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <ProductTable analytics={analytics} />
        <ChannelTable analytics={analytics} />
      </section>
    </>
  );
}

function DateField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="text-sm font-semibold">{label}<input className="mt-1 block w-full rounded-lg border border-[var(--border)] px-3 py-2 font-normal" type="date" value={value} onChange={(event) => onChange(event.target.value)} /></label>;
}

function MetricCard({ label, value, margin, comparison, prominent = false }: { label: string; value: number; margin?: number | null; comparison?: MetricComparison; prominent?: boolean }) {
  return (
    <Card className={`p-5 ${prominent ? "border-green-700 bg-green-900 text-white" : ""}`}>
      <p className={`text-sm ${prominent ? "text-green-100" : "text-[var(--muted)]"}`}>{label}</p>
      <p className="mt-2 text-2xl font-bold">{money.format(value)}</p>
      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
        {margin !== undefined && <span>Biên {formatBps(margin)}</span>}
        {comparison && <ComparisonBadge comparison={comparison} dark={prominent} />}
      </div>
    </Card>
  );
}

function ComparisonBadge({ comparison, dark }: { comparison: MetricComparison; dark: boolean }) {
  if (comparison.change_bps === null) return <span className={dark ? "text-green-100" : "text-[var(--muted)]"}>Kỳ trước chưa có dữ liệu</span>;
  const positive = comparison.difference >= 0;
  return <span className={`rounded-full px-2 py-1 font-semibold ${dark ? "bg-white/15 text-white" : positive ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>{positive ? "↑" : "↓"} {formatBps(Math.abs(comparison.change_bps))} so với kỳ trước</span>;
}

function TrendChart({ points }: { points: TrendPoint[] }) {
  const maximum = Math.max(1, ...points.flatMap((point) => [point.revenue, Math.abs(point.net_profit)]));
  return (
    <Card className="mt-6 overflow-hidden p-5 sm:p-7">
      <h2 className="text-xl font-bold">Xu hướng theo ngày</h2>
      <p className="mt-1 text-sm text-[var(--muted)]">Xanh nhạt: doanh thu · Xanh đậm: lợi nhuận ròng · Đỏ: lỗ ròng</p>
      <div className="mt-6 overflow-x-auto pb-2">
        <div className="flex h-52 min-w-max items-end gap-2 border-b border-[var(--border)] px-1">
          {points.map((point) => (
            <div key={point.date} className="flex w-12 shrink-0 flex-col items-center justify-end gap-1" title={`${point.date}: doanh thu ${money.format(point.revenue)}, lợi nhuận ${money.format(point.net_profit)}`}>
              <div className="flex h-40 items-end gap-1">
                <div className="w-3 rounded-t bg-green-300" style={{ height: `${Math.max(2, point.revenue / maximum * 100)}%` }} />
                <div className={`w-3 rounded-t ${point.net_profit >= 0 ? "bg-green-800" : "bg-red-600"}`} style={{ height: `${Math.max(2, Math.abs(point.net_profit) / maximum * 100)}%` }} />
              </div>
              <span className="text-[10px] text-[var(--muted)]">{point.date.slice(5).replace("-", "/")}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function ProductTable({ analytics }: { analytics: Analytics }) {
  return (
    <DataCard title="Lợi nhuận theo sản phẩm" empty={analytics.products.length === 0}>
      <table className="w-full min-w-[560px] text-left text-sm">
        <thead className="text-[var(--muted)]">
          <tr>
            <th className="pb-3">Sản phẩm</th>
            <th className="pb-3 text-right">SL</th>
            <th className="pb-3 text-right">Doanh thu</th>
            <th className="pb-3 text-right">Lãi gộp</th>
          </tr>
        </thead>
        <tbody>
          {analytics.products.map((product) => {
            const isLoss = product.gross_profit < 0;
            return (
              <tr key={`${product.sku}-${product.name}`} className="border-t border-[var(--border)]">
                <td className="py-3">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold">{product.name}</p>
                    {isLoss && (
                      <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-extrabold text-red-700">
                        Lỗ ⚠️
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[var(--muted)]">{product.sku || "Không SKU"}</p>
                </td>
                <td className="py-3 text-right">{product.quantity}</td>
                <td className="py-3 text-right">{money.format(product.revenue)}</td>
                <td className={`py-3 text-right font-semibold ${isLoss ? "text-red-700" : "text-emerald-800"}`}>
                  {money.format(product.gross_profit)}
                  <p className={`text-xs font-normal ${isLoss ? "text-red-600" : "text-[var(--muted)]"}`}>
                    {formatBps(product.gross_margin_bps)}
                  </p>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </DataCard>
  );
}

function ChannelTable({ analytics }: { analytics: Analytics }) {
  return (
    <DataCard title="Hiệu quả theo kênh bán" empty={analytics.channels.length === 0}>
      <table className="w-full min-w-[520px] text-left text-sm">
        <thead className="text-[var(--muted)]">
          <tr>
            <th className="pb-3">Kênh</th>
            <th className="pb-3 text-right">Đơn</th>
            <th className="pb-3 text-right">Phí</th>
            <th className="pb-3 text-right">Lãi đóng góp</th>
          </tr>
        </thead>
        <tbody>
          {analytics.channels.map((channel) => {
            const isShopee = channel.channel.toUpperCase() === "SHOPEE";
            const isTikTok = channel.channel.toUpperCase() === "TIKTOK";
            return (
              <tr key={channel.channel} className="border-t border-[var(--border)]">
                <td className="py-3">
                  <span
                    className={`inline-block rounded-full px-2.5 py-1 text-xs font-bold ${
                      isShopee
                        ? "bg-orange-100 text-orange-800"
                        : isTikTok
                          ? "bg-slate-900 text-white"
                          : "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {channel.channel}
                  </span>
                </td>
                <td className="py-3 text-right font-medium">{channel.order_count}</td>
                <td className="py-3 text-right text-red-700 font-medium">{money.format(channel.fees)}</td>
                <td className="py-3 text-right font-extrabold text-emerald-800">
                  {money.format(channel.contribution_profit)}
                  <p className="text-xs font-normal text-[var(--muted)]">
                    {formatBps(channel.contribution_margin_bps)}
                  </p>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </DataCard>
  );
}

function DataCard({ title, empty, children }: { title: string; empty: boolean; children: React.ReactNode }) {
  return <Card className="overflow-hidden p-5 sm:p-7"><h2 className="text-xl font-bold">{title}</h2>{empty ? <p className="mt-6 text-sm text-[var(--muted)]">Chưa có dữ liệu bán hàng.</p> : <div className="mt-5 overflow-x-auto">{children}</div>}</Card>;
}

function formatBps(value: number | null) {
  return value === null ? "—" : `${(value / 100).toLocaleString("vi-VN", { maximumFractionDigits: 2 })}%`;
}

function Status({ message, action }: { message: string; action?: () => void }) {
  return <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-6 text-center text-[var(--muted)]"><p>{message}</p>{action && <Button onClick={action}>Đăng nhập lại</Button>}</main>;
}
