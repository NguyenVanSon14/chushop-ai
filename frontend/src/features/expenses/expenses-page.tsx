"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useHasAccessToken } from "@/features/auth/use-auth-token";
import { useActiveBusiness, useBusinesses } from "@/features/businesses/hooks";
import type { Expense } from "@/lib/api/types";
import { ExpenseForm } from "./expense-form";
import { useDeleteExpense, useExpenses } from "./hooks";

const money = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
});

export function ExpensesPage() {
  const router = useRouter();
  const authenticated = useHasAccessToken();
  const businesses = useBusinesses(authenticated);
  const business = useActiveBusiness(businesses.data);
  const expenses = useExpenses(business?.id);
  const deleteMutation = useDeleteExpense(business?.id ?? "");
  const [editing, setEditing] = useState<Expense | null>(null);

  useEffect(() => {
    if (!authenticated) router.replace("/login");
  }, [authenticated, router]);

  function remove(expense: Expense) {
    if (window.confirm(`Xóa chi phí “${expense.description}”?`)) {
      deleteMutation.mutate(expense.id);
    }
  }

  if (!authenticated || businesses.isLoading) return <Status text="Đang tải doanh nghiệp..." />;
  if (!business) return <Status text="Bạn cần tạo doanh nghiệp trước." />;
  const total = expenses.data?.reduce((sum, expense) => sum + expense.amount, 0) ?? 0;

  return (
    <AppShell businessId={business.id} businessName={business.name} businesses={businesses.data ?? []}>
      <div>
        <PageTitle
          eyebrow="Dữ liệu tiền"
          title="Chi phí"
          description="Theo dõi chi phí vận hành để lợi nhuận ròng luôn phản ánh đúng thực tế."
        />

        <div className="mt-8 grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
          <section className="order-2 xl:order-1">
            <div className="mb-4 flex items-end justify-between gap-4">
              <div><h2 className="text-xl font-bold">Lịch sử chi phí</h2><p className="mt-1 text-sm text-[var(--muted)]">{expenses.data?.length ?? 0} khoản đã ghi nhận</p></div>
              <div className="rounded-xl bg-red-50 px-4 py-2 text-right"><p className="text-[10px] font-bold uppercase tracking-wide text-red-500">Tổng chi</p><p className="font-extrabold text-red-700">{money.format(total)}</p></div>
            </div>
            {expenses.isLoading && <Card className="p-10 text-center text-[var(--muted)]">Đang tải chi phí...</Card>}
            {expenses.isError && <Card className="p-10 text-center text-red-700">Không thể tải chi phí.</Card>}
            {expenses.data?.length === 0 && <Card className="p-10 text-center"><p className="font-bold">Chưa có chi phí</p><p className="mt-2 text-sm text-[var(--muted)]">Thêm khoản chi đầu tiên bằng biểu mẫu bên cạnh.</p></Card>}
            <div className="grid gap-3">
              {expenses.data?.map((expense) => (
                <Card key={expense.id} className="group grid gap-4 p-5 transition hover:border-emerald-200 hover:shadow-md sm:grid-cols-[1fr_auto_auto] sm:items-center">
                  <div><div className="flex items-center gap-3"><span className="grid size-10 shrink-0 place-items-center rounded-xl bg-amber-50 text-lg">↗</span><div><h3 className="font-bold">{expense.description}</h3><p className="mt-1 text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">{expense.category} · {new Date(`${expense.incurred_on}T00:00:00`).toLocaleDateString("vi-VN")}</p></div></div></div>
                  <p className="font-extrabold text-red-700 sm:text-right">−{money.format(expense.amount)}</p>
                  <div className="flex gap-2 sm:justify-end"><Button className="h-9 bg-white px-3 text-emerald-800 ring-1 ring-emerald-700/30 hover:bg-emerald-50" onClick={() => setEditing(expense)}>Sửa</Button><Button className="h-9 bg-white px-3 text-red-700 ring-1 ring-red-200 hover:bg-red-50" disabled={deleteMutation.isPending} onClick={() => remove(expense)}>Xóa</Button></div>
                </Card>
              ))}
            </div>
          </section>

          <Card className="order-1 h-fit p-5 xl:sticky xl:top-6 xl:order-2 sm:p-6">
            <div className="mb-5"><p className="text-xs font-bold uppercase tracking-[0.14em] text-emerald-700">Ghi nhận</p><h2 className="mt-1 text-xl font-bold">{editing ? `Sửa ${editing.description}` : "Thêm chi phí"}</h2></div>
            <ExpenseForm key={editing?.id ?? "new"} businessId={business.id} expense={editing} onDone={() => setEditing(null)} />
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

function PageTitle({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <div><p className="text-xs font-extrabold uppercase tracking-[0.18em] text-emerald-700">{eyebrow}</p><h1 className="mt-2 text-3xl font-extrabold tracking-tight sm:text-4xl">{title}</h1><p className="mt-3 max-w-2xl text-[var(--muted)]">{description}</p></div>;
}

function Status({ text }: { text: string }) {
  return <main className="flex min-h-screen items-center justify-center p-6 text-[var(--muted)]">{text}</main>;
}
