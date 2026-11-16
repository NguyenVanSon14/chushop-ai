"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { getMe } from "@/features/auth/api";
import { selectActiveBusiness } from "@/features/businesses/hooks";
import type { Business } from "@/lib/api/types";
import { clearAccessToken } from "@/lib/auth/token-storage";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/dashboard", label: "Tổng quan", shortLabel: "Tổng quan", icon: "dashboard" },
  { href: "/products", label: "Sản phẩm", shortLabel: "Sản phẩm", icon: "products" },
  { href: "/sales", label: "Bán hàng", shortLabel: "Bán hàng", icon: "sales" },
  { href: "/expenses", label: "Chi phí", shortLabel: "Chi phí", icon: "expenses" },
  { href: "/assistant", label: "Trợ lý AI", shortLabel: "Trợ lý", icon: "assistant" },
] as const;

export function AppShell({
  businessName,
  businessId,
  businesses,
  children,
  wide = false,
}: {
  businessName: string;
  businessId: string;
  businesses: Business[];
  children: ReactNode;
  wide?: boolean;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const currentUser = useQuery({ queryKey: ["auth", "me"], queryFn: getMe });

  function logout() {
    clearAccessToken();
    router.replace("/login");
  }

  function changeBusiness(businessId: string) {
    selectActiveBusiness(businessId);
    window.location.assign(pathname);
  }

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[252px_minmax(0,1fr)]">
      <aside className="sticky top-0 hidden h-screen flex-col border-r border-emerald-950/10 bg-[#073d2d] px-4 py-5 text-white lg:flex">
        <Link href="/dashboard" className="flex items-center gap-3 rounded-2xl px-3 py-2">
          <BrandMark />
          <div>
            <p className="text-lg font-extrabold tracking-tight">ChủShop AI</p>
            <p className="text-xs text-emerald-200/70">Money Brain</p>
          </div>
        </Link>

        <div className="mt-6 rounded-2xl border border-white/10 bg-white/8 p-3">
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-emerald-200/60">
            Doanh nghiệp
          </p>
          {businesses.length > 1 ? (
            <select
              aria-label="Chọn doanh nghiệp"
              className="mt-2 w-full rounded-lg border border-white/15 bg-emerald-950/40 px-2 py-2 text-sm font-semibold text-white outline-none focus:border-emerald-300"
              onChange={(event) => changeBusiness(event.target.value)}
              value={businessId}
            >
              {businesses.map((business) => <option key={business.id} className="bg-emerald-950" value={business.id}>{business.name}</option>)}
            </select>
          ) : (
            <p className="mt-1 truncate text-sm font-semibold" title={businessName}>{businessName}</p>
          )}
          <div className="mt-3 flex items-center gap-2 text-xs text-emerald-100/70">
            <span className="size-2 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,.8)]" />
            Dữ liệu đang được bảo vệ
          </div>
        </div>

        <nav className="mt-6 space-y-1" aria-label="Điều hướng chính">
          {navigation.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold transition",
                  active
                    ? "bg-white text-emerald-950 shadow-lg shadow-black/10"
                    : "text-emerald-50/75 hover:bg-white/10 hover:text-white",
                )}
              >
                <NavIcon name={item.icon} />
                {item.label}
                {item.icon === "assistant" && (
                  <span className={cn("ml-auto rounded-full px-2 py-0.5 text-[10px]", active ? "bg-emerald-100 text-emerald-800" : "bg-emerald-400/15 text-emerald-200")}>AI</span>
                )}
              </Link>
            );
          })}
        </nav>

        {currentUser.data?.is_platform_admin && (
          <Link className="mt-auto flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-emerald-100/70 transition hover:bg-white/10 hover:text-white" href="/admin">
            <NavIcon name="admin" /> Quản trị hệ thống
          </Link>
        )}
        <button className={cn("flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-emerald-100/70 transition hover:bg-white/10 hover:text-white", !currentUser.data?.is_platform_admin && "mt-auto")} onClick={logout} type="button">
          <NavIcon name="logout" /> Đăng xuất
        </button>
      </aside>

      <div className="min-w-0">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[var(--border)] bg-white/90 px-5 backdrop-blur-xl lg:hidden">
          <Link href="/dashboard" className="flex items-center gap-2.5"><BrandMark small /><span className="font-extrabold tracking-tight text-emerald-950">ChủShop AI</span></Link>
          <div className="flex items-center gap-2">
            {currentUser.data?.is_platform_admin && <Link aria-label="Quản trị hệ thống" className="grid size-9 place-items-center rounded-xl text-[var(--muted)] transition hover:bg-emerald-50 hover:text-emerald-800" href="/admin"><NavIcon name="admin" /></Link>}
            {businesses.length > 1 ? (
              <select aria-label="Chọn doanh nghiệp" className="max-w-36 rounded-lg border border-[var(--border)] bg-white px-2 py-1.5 text-xs font-semibold outline-none" onChange={(event) => changeBusiness(event.target.value)} value={businessId}>{businesses.map((business) => <option key={business.id} value={business.id}>{business.name}</option>)}</select>
            ) : (
              <p className="hidden max-w-32 truncate text-xs font-semibold text-[var(--muted)] sm:block">{businessName}</p>
            )}
            <button aria-label="Đăng xuất" className="grid size-9 place-items-center rounded-xl text-[var(--muted)] transition hover:bg-red-50 hover:text-red-700" onClick={logout} type="button"><NavIcon name="logout" /></button>
          </div>
        </header>
        <main className={cn("mx-auto px-5 py-7 pb-28 sm:px-8 sm:py-10 lg:pb-12", wide ? "max-w-[1500px]" : "max-w-7xl")}>{children}</main>
      </div>

      <nav className="fixed inset-x-3 bottom-3 z-40 grid grid-cols-5 rounded-2xl border border-white/60 bg-[#073d2d]/95 p-1.5 text-white shadow-2xl shadow-emerald-950/30 backdrop-blur-xl lg:hidden" aria-label="Điều hướng di động">
        {navigation.map((item) => {
          const active = pathname === item.href;
          return <Link key={item.href} href={item.href} className={cn("flex min-w-0 flex-col items-center gap-1 rounded-xl px-1 py-2 text-[10px] font-semibold transition", active ? "bg-white text-emerald-950" : "text-emerald-100/70")}><NavIcon name={item.icon} /><span className="truncate">{item.shortLabel}</span></Link>;
        })}
      </nav>
    </div>
  );
}

function BrandMark({ small = false }: { small?: boolean }) {
  return <span className={cn("grid shrink-0 place-items-center rounded-xl bg-gradient-to-br from-emerald-300 to-lime-300 font-black text-emerald-950 shadow-lg shadow-emerald-950/20", small ? "size-9 text-sm" : "size-11")}>CS</span>;
}

function NavIcon({ name }: { name: string }) {
  const paths: Record<string, ReactNode> = {
    dashboard: <><path d="M4 13h6V4H4v9Zm0 7h6v-4H4v4Zm10 0h6v-9h-6v9Zm0-16v4h6V4h-6Z" /></>,
    products: <><path d="m4 7 8-4 8 4-8 4-8-4Z" /><path d="m4 7 8 4 8-4M4 12l8 4 8-4M4 17l8 4 8-4" /></>,
    sales: <><path d="M4 19V9m6 10V5m6 14v-7m4 7H2" /></>,
    expenses: <><path d="M4 6h16v12H4z" /><path d="M4 10h16M8 14h3" /></>,
    assistant: <><path d="M12 3a7 7 0 0 0-7 7v2a4 4 0 0 0 4 4h1l2 4 2-4h1a4 4 0 0 0 4-4v-2a7 7 0 0 0-7-7Z" /><path d="M9 10h.01M15 10h.01" /></>,
    admin: <><path d="M12 3 5 6v5c0 4.6 2.8 8 7 10 4.2-2 7-5.4 7-10V6l-7-3Z" /><path d="m9 12 2 2 4-4" /></>,
    logout: <><path d="M10 17l5-5-5-5M15 12H3M14 4h5a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-5" /></>,
  };
  return <svg aria-hidden className="size-5 shrink-0" fill={name === "dashboard" ? "currentColor" : "none"} stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" viewBox="0 0 24 24">{paths[name]}</svg>;
}
