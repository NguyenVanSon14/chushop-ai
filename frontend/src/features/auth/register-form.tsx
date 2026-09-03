"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api/client";
import { setAccessToken } from "@/lib/auth/token-storage";
import { login, register } from "./api";
import { registerSchema } from "./schemas";

export function RegisterForm() {
  const router = useRouter();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const mutation = useMutation({
    mutationFn: async (input: { email: string; password: string; full_name: string }) => {
      await register(input);
      return login({ email: input.email, password: input.password });
    },
    onSuccess: (result) => {
      setAccessToken(result.access_token);
      router.replace("/onboarding/business");
    },
  });

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsed = registerSchema.safeParse(Object.fromEntries(new FormData(event.currentTarget)));
    if (!parsed.success) {
      setErrors(Object.fromEntries(parsed.error.issues.map((issue) => [issue.path[0], issue.message])));
      return;
    }
    setErrors({});
    mutation.mutate(parsed.data);
  }

  return (
    <form onSubmit={submit} className="space-y-5" noValidate>
      <Field label="Họ và tên" error={errors.full_name}><Input name="full_name" autoComplete="name" /></Field>
      <Field label="Email" error={errors.email}><Input name="email" type="email" autoComplete="email" /></Field>
      <Field label="Mật khẩu" error={errors.password}><Input name="password" type="password" autoComplete="new-password" /></Field>
      {mutation.isError && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{mutation.error instanceof ApiError ? mutation.error.message : "Không thể tạo tài khoản"}</p>}
      <Button className="w-full" disabled={mutation.isPending}>{mutation.isPending ? "Đang tạo tài khoản..." : "Tạo tài khoản"}</Button>
    </form>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return <label className="block space-y-2"><span className="text-sm font-semibold">{label}</span>{children}{error && <span className="block text-sm text-red-600">{error}</span>}</label>;
}

export const RegisterFooter = () => <>Đã có tài khoản? <Link className="font-semibold text-green-700 hover:underline" href="/login">Đăng nhập</Link></>;
