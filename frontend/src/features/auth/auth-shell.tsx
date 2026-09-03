import Link from "next/link";
import { Card } from "@/components/ui/card";

export function AuthShell({
  title,
  subtitle,
  footer,
  children,
}: {
  title: string;
  subtitle: string;
  footer: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <main className="grid min-h-screen lg:grid-cols-2">
      <section className="hidden bg-green-950 p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <Link href="/" className="text-xl font-bold">ChủShop AI</Link>
        <div className="max-w-lg">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-green-300">Money Brain v0.1</p>
          <h2 className="text-5xl font-bold leading-tight">Hiểu dòng tiền. Điều hành tự tin.</h2>
          <p className="mt-5 text-lg text-green-100/80">Nền tảng tài chính gọn gàng dành cho chủ shop Việt.</p>
        </div>
        <p className="text-sm text-green-200/70">Dữ liệu của mỗi doanh nghiệp được tách biệt và bảo vệ.</p>
      </section>
      <section className="flex items-center justify-center p-5 sm:p-10">
        <Card className="w-full max-w-md p-6 sm:p-8">
          <div className="mb-7 lg:hidden"><span className="text-lg font-bold text-green-800">ChủShop AI</span></div>
          <h1 className="text-3xl font-bold">{title}</h1>
          <p className="mt-2 text-[var(--muted)]">{subtitle}</p>
          <div className="mt-7">{children}</div>
          <div className="mt-6 text-center text-sm text-[var(--muted)]">{footer}</div>
        </Card>
      </section>
    </main>
  );
}
