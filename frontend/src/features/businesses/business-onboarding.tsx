"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useHasAccessToken } from "@/features/auth/use-auth-token";
import { ApiError } from "@/lib/api/client";
import { useBusinesses, useCreateBusiness } from "./hooks";

const schema = z.object({ name: z.string().trim().min(2, "Tên doanh nghiệp cần ít nhất 2 ký tự").max(255) });

export function BusinessOnboarding() {
  const router = useRouter();
  const authenticated = useHasAccessToken();
  const [validationError, setValidationError] = useState("");
  const businesses = useBusinesses(authenticated);
  const createMutation = useCreateBusiness();

  useEffect(() => {
    if (!authenticated) router.replace("/login");
  }, [authenticated, router]);

  useEffect(() => {
    if (businesses.data?.length) router.replace("/dashboard");
  }, [businesses.data, router]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsed = schema.safeParse(Object.fromEntries(new FormData(event.currentTarget)));
    if (!parsed.success) {
      setValidationError(parsed.error.issues[0]?.message ?? "Tên doanh nghiệp không hợp lệ");
      return;
    }
    setValidationError("");
    createMutation.mutate(parsed.data.name, { onSuccess: () => router.replace("/dashboard") });
  }

  if (!authenticated || businesses.isLoading) {
    return <CenteredMessage message="Đang tải thông tin doanh nghiệp..." />;
  }
  if (businesses.isError) {
    return <CenteredMessage message="Không thể tải dữ liệu. Vui lòng đăng nhập lại." />;
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-5">
      <Card className="w-full max-w-xl p-6 sm:p-10">
        <p className="text-sm font-bold uppercase tracking-[0.18em] text-green-700">Bước đầu tiên</p>
        <h1 className="mt-3 text-3xl font-bold sm:text-4xl">Thiết lập doanh nghiệp</h1>
        <p className="mt-3 text-[var(--muted)]">Thông tin này giúp ChủShop tổ chức dữ liệu đúng theo từng cửa hàng.</p>
        <form onSubmit={submit} className="mt-8 space-y-5" noValidate>
          <label className="block space-y-2">
            <span className="text-sm font-semibold">Tên doanh nghiệp hoặc cửa hàng</span>
            <Input name="name" placeholder="Ví dụ: Tiệm Nhà Mình" autoFocus />
            {validationError && <span className="block text-sm text-red-600">{validationError}</span>}
          </label>
          {createMutation.isError && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{createMutation.error instanceof ApiError ? createMutation.error.message : "Không thể tạo doanh nghiệp"}</p>}
          <Button className="w-full" disabled={createMutation.isPending}>{createMutation.isPending ? "Đang khởi tạo..." : "Tạo doanh nghiệp"}</Button>
        </form>
      </Card>
    </main>
  );
}

function CenteredMessage({ message }: { message: string }) {
  return <main className="flex min-h-screen items-center justify-center p-6 text-center text-[var(--muted)]">{message}</main>;
}
