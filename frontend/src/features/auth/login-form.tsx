"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { listBusinesses } from "@/features/businesses/api";
import { ApiError } from "@/lib/api/client";
import { setAccessToken } from "@/lib/auth/token-storage";
import { login } from "./api";
import { loginSchema } from "./schemas";

export function LoginForm() {
  const router = useRouter();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const mutation = useMutation({
    mutationFn: login,
    onSuccess: async (result) => {
      setAccessToken(result.access_token);
      const businesses = await listBusinesses();
      router.replace(businesses.length ? "/dashboard" : "/onboarding/business");
    },
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const parsed = loginSchema.safeParse(data);
    if (!parsed.success) {
      setErrors(Object.fromEntries(parsed.error.issues.map((issue) => [issue.path[0], issue.message])));
      return;
    }
    setErrors({});
    mutation.mutate(parsed.data);
  }

  return (
    <form onSubmit={submit} className="space-y-5" noValidate>
      <Field label="Email" error={errors.email}><Input name="email" type="email" autoComplete="email" /></Field>
      <Field label="Mật khẩu" error={errors.password}><Input name="password" type="password" autoComplete="current-password" /></Field>
      {mutation.isError && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{mutation.error instanceof ApiError ? mutation.error.message : "Đăng nhập không thành công"}</p>}
      <Button className="w-full" disabled={mutation.isPending}>{mutation.isPending ? "Đang đăng nhập..." : "Đăng nhập"}</Button>
    </form>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return <label className="block space-y-2"><span className="text-sm font-semibold">{label}</span>{children}{error && <span className="block text-sm text-red-600">{error}</span>}</label>;
}

export const LoginFooter = () => <>Chưa có tài khoản? <Link className="font-semibold text-green-700 hover:underline" href="/register">Đăng ký miễn phí</Link></>;
