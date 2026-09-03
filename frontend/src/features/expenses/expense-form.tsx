"use client";

import { FormEvent, useState } from "react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api/client";
import type { Expense } from "@/lib/api/types";
import type { ExpenseInput } from "./api";
import { useCreateExpense, useUpdateExpense } from "./hooks";

const schema = z.object({
  description: z.string().trim().min(1, "Vui lòng nhập nội dung").max(255),
  category: z.string().trim().min(1, "Vui lòng nhập nhóm chi phí").max(100),
  amount: z.coerce.number().int("Số tiền phải là số nguyên").positive("Số tiền phải lớn hơn 0"),
  incurred_on: z.string().date("Ngày không hợp lệ"),
});

export function ExpenseForm({ businessId, expense, onDone }: { businessId: string; expense: Expense | null; onDone: () => void }) {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const createMutation = useCreateExpense(businessId);
  const updateMutation = useUpdateExpense(businessId);
  const mutation = expense ? updateMutation : createMutation;

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const parsed = schema.safeParse(Object.fromEntries(new FormData(form)));
    if (!parsed.success) {
      setErrors(Object.fromEntries(parsed.error.issues.map((issue) => [issue.path[0], issue.message])));
      return;
    }
    setErrors({});
    const input: ExpenseInput = parsed.data;
    const options = { onSuccess: () => { form.reset(); onDone(); } };
    if (expense) updateMutation.mutate({ id: expense.id, input }, options);
    else createMutation.mutate(input, options);
  }

  return <form onSubmit={submit} className="space-y-5" noValidate><div className="grid gap-4 sm:grid-cols-2"><Field label="Nội dung" error={errors.description} className="sm:col-span-2"><Input name="description" defaultValue={expense?.description} placeholder="Ví dụ: Quảng cáo tháng 9" /></Field><Field label="Nhóm chi phí" error={errors.category}><Input name="category" defaultValue={expense?.category} placeholder="MARKETING" /></Field><Field label="Ngày phát sinh" error={errors.incurred_on}><Input name="incurred_on" type="date" defaultValue={expense?.incurred_on ?? new Date().toISOString().slice(0, 10)} /></Field><Field label="Số tiền (VND)" error={errors.amount} className="sm:col-span-2"><Input name="amount" type="number" min="1" step="1" defaultValue={expense?.amount ?? ""} /></Field></div>{mutation.isError && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{mutation.error instanceof ApiError ? mutation.error.message : "Không thể lưu chi phí"}</p>}<div className="flex gap-3"><Button disabled={mutation.isPending}>{mutation.isPending ? "Đang lưu..." : expense ? "Lưu thay đổi" : "Thêm chi phí"}</Button>{expense && <Button type="button" onClick={onDone} className="bg-white text-green-800 ring-1 ring-green-800 hover:bg-green-50">Hủy</Button>}</div></form>;
}

function Field({ label, error, className = "", children }: { label: string; error?: string; className?: string; children: React.ReactNode }) { return <label className={`block space-y-2 ${className}`}><span className="text-sm font-semibold">{label}</span>{children}{error && <span className="block text-sm text-red-600">{error}</span>}</label>; }
