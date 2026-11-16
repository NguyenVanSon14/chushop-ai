"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getMe } from "@/features/auth/api";
import { useHasAccessToken } from "@/features/auth/use-auth-token";
import { clearAccessToken } from "@/lib/auth/token-storage";
import {
  useAdminAuditLogs,
  useAdminBusinesses,
  useAdminUsers,
  useUpdateAdminUserStatus,
} from "./hooks";

const dateTime = new Intl.DateTimeFormat("vi-VN", {
  dateStyle: "short",
  timeStyle: "short",
});

export function AdminPage() {
  const router = useRouter();
  const authenticated = useHasAccessToken();
  const currentUser = useQuery({
    queryKey: ["auth", "me"],
    queryFn: getMe,
    enabled: authenticated,
  });
  const enabled = Boolean(currentUser.data?.is_platform_admin);
  const users = useAdminUsers(enabled);
  const businesses = useAdminBusinesses(enabled);
  const logs = useAdminAuditLogs(enabled);
  const updateStatus = useUpdateAdminUserStatus();

  useEffect(() => {
    if (!authenticated) router.replace("/login");
  }, [authenticated, router]);

  function logout() {
    clearAccessToken();
    router.replace("/login");
  }

  if (!authenticated || currentUser.isLoading) {
    return <PageStatus message="Đang kiểm tra quyền quản trị..." />;
  }
  if (currentUser.isError) {
    return <PageStatus message="Phiên đăng nhập đã hết hạn." action={logout} />;
  }
  if (!enabled) {
    return (
      <PageStatus
        message="Tài khoản này không có quyền quản trị hệ thống ChủShop AI."
        href="/dashboard"
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f7f5]">
      <header className="border-b border-emerald-950/10 bg-[#073d2d] text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
          <div>
            <p className="text-lg font-extrabold">ChủShop AI</p>
            <p className="text-xs text-emerald-200/70">Quản trị hệ thống</p>
          </div>
          <div className="flex items-center gap-2">
            <Link className="rounded-xl px-4 py-2 text-sm font-semibold hover:bg-white/10" href="/dashboard">
              Về Money Brain
            </Link>
            <button className="rounded-xl px-4 py-2 text-sm font-semibold text-emerald-100/80 hover:bg-white/10" onClick={logout} type="button">
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8 sm:px-8">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.16em] text-emerald-700">Platform Admin</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">Tổng quan hệ thống</h1>
          <p className="mt-2 text-slate-600">Quản lý tài khoản, doanh nghiệp và theo dõi thao tác quản trị.</p>
        </div>

        <section className="mt-7 grid gap-4 sm:grid-cols-3">
          <Stat label="Người dùng" value={users.data?.length} loading={users.isLoading} />
          <Stat label="Doanh nghiệp" value={businesses.data?.length} loading={businesses.isLoading} />
          <Stat label="Thao tác gần đây" value={logs.data?.length} loading={logs.isLoading} />
        </section>

        {(users.isError || businesses.isError || logs.isError) && (
          <Card className="mt-6 border-red-200 bg-red-50 p-5 text-sm text-red-800">
            Không thể tải đầy đủ dữ liệu quản trị. Hãy thử tải lại trang.
          </Card>
        )}

        <section className="mt-7 grid gap-7 xl:grid-cols-[1.35fr_.65fr]">
          <Card className="overflow-hidden">
            <div className="border-b border-[var(--border)] p-5 sm:p-6">
              <h2 className="text-xl font-bold">Tài khoản</h2>
              <p className="mt-1 text-sm text-slate-500">Khóa hoặc mở lại quyền đăng nhập của người dùng.</p>
            </div>
            {users.isLoading ? (
              <Empty text="Đang tải tài khoản..." />
            ) : users.data?.length ? (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px] text-left text-sm">
                  <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                    <tr><th className="px-5 py-3">Người dùng</th><th className="px-5 py-3">Quyền</th><th className="px-5 py-3">Trạng thái</th><th className="px-5 py-3 text-right">Thao tác</th></tr>
                  </thead>
                  <tbody>
                    {users.data.map((user) => {
                      const isSelf = user.id === currentUser.data?.id;
                      return (
                        <tr className="border-t border-[var(--border)]" key={user.id}>
                          <td className="px-5 py-4"><p className="font-semibold text-slate-900">{user.full_name}</p><p className="mt-0.5 text-xs text-slate-500">{user.email}</p></td>
                          <td className="px-5 py-4"><Badge tone={user.is_platform_admin ? "green" : "gray"}>{user.is_platform_admin ? "Platform admin" : "Người dùng"}</Badge></td>
                          <td className="px-5 py-4"><Badge tone={user.is_active ? "green" : "red"}>{user.is_active ? "Đang hoạt động" : "Đã khóa"}</Badge></td>
                          <td className="px-5 py-4 text-right">
                            <button
                              className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
                              disabled={isSelf || updateStatus.isPending}
                              onClick={() => updateStatus.mutate({ userId: user.id, isActive: !user.is_active })}
                              type="button"
                            >
                              {isSelf ? "Tài khoản hiện tại" : user.is_active ? "Khóa tài khoản" : "Mở lại"}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : <Empty text="Chưa có tài khoản." />}
            {updateStatus.isError && <p className="border-t border-red-100 bg-red-50 px-5 py-3 text-sm text-red-700">Không thể cập nhật tài khoản. Vui lòng thử lại.</p>}
          </Card>

          <Card className="overflow-hidden">
            <div className="border-b border-[var(--border)] p-5 sm:p-6"><h2 className="text-xl font-bold">Doanh nghiệp</h2><p className="mt-1 text-sm text-slate-500">Các không gian đang có trên hệ thống.</p></div>
            {businesses.isLoading ? <Empty text="Đang tải doanh nghiệp..." /> : businesses.data?.length ? (
              <div className="divide-y divide-[var(--border)]">
                {businesses.data.map((business) => <div className="p-5" key={business.id}><p className="font-semibold text-slate-900">{business.name}</p><p className="mt-1 text-xs text-slate-500">{business.slug} · {business.currency} · {business.timezone}</p></div>)}
              </div>
            ) : <Empty text="Chưa có doanh nghiệp." />}
          </Card>
        </section>

        <Card className="mt-7 overflow-hidden">
          <div className="border-b border-[var(--border)] p-5 sm:p-6"><h2 className="text-xl font-bold">Nhật ký quản trị</h2><p className="mt-1 text-sm text-slate-500">100 thao tác mới nhất, chỉ đọc.</p></div>
          {logs.isLoading ? <Empty text="Đang tải nhật ký..." /> : logs.data?.length ? (
            <div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm"><thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr><th className="px-5 py-3">Thời gian</th><th className="px-5 py-3">Hành động</th><th className="px-5 py-3">Đối tượng</th><th className="px-5 py-3">Người thực hiện</th></tr></thead><tbody>{logs.data.map((log) => <tr className="border-t border-[var(--border)]" key={log.id}><td className="px-5 py-4 text-slate-600">{dateTime.format(new Date(log.created_at))}</td><td className="px-5 py-4 font-semibold">{log.action}</td><td className="px-5 py-4 text-slate-600">{log.target_type} · {log.target_id}</td><td className="px-5 py-4 font-mono text-xs text-slate-500">{log.actor_user_id}</td></tr>)}</tbody></table></div>
          ) : <Empty text="Chưa có thao tác quản trị." />}
        </Card>
      </main>
    </div>
  );
}

function Stat({ label, value, loading }: { label: string; value?: number; loading: boolean }) {
  return <Card className="p-5"><p className="text-sm text-slate-500">{label}</p><p className="mt-2 text-3xl font-extrabold text-emerald-950">{loading ? "—" : (value ?? 0).toLocaleString("vi-VN")}</p></Card>;
}

function Badge({ children, tone }: { children: React.ReactNode; tone: "green" | "red" | "gray" }) {
  const styles = { green: "bg-emerald-50 text-emerald-700", red: "bg-red-50 text-red-700", gray: "bg-slate-100 text-slate-600" };
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${styles[tone]}`}>{children}</span>;
}

function Empty({ text }: { text: string }) {
  return <p className="p-8 text-center text-sm text-slate-500">{text}</p>;
}

function PageStatus({ message, action, href }: { message: string; action?: () => void; href?: string }) {
  return <main className="flex min-h-screen flex-col items-center justify-center gap-5 bg-[#f4f7f5] p-6 text-center"><p className="max-w-md text-slate-600">{message}</p>{action && <Button onClick={action}>Đăng nhập lại</Button>}{href && <Link className="rounded-xl bg-emerald-800 px-5 py-3 font-semibold text-white" href={href}>Về trang tổng quan</Link>}</main>;
}
