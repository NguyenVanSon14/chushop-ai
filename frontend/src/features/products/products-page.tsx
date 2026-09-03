"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useHasAccessToken } from "@/features/auth/use-auth-token";
import { useActiveBusiness, useBusinesses } from "@/features/businesses/hooks";
import type { Product } from "@/lib/api/types";
import { ProductForm } from "./product-form";
import { useDeleteProduct, useProducts } from "./hooks";

const moneyFormatter = new Intl.NumberFormat("vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0,
});

export function ProductsPage() {
  const router = useRouter();
  const authenticated = useHasAccessToken();
  const businesses = useBusinesses(authenticated);
  const business = useActiveBusiness(businesses.data);
  const products = useProducts(business?.id);
  const deleteMutation = useDeleteProduct(business?.id ?? "");
  const [editing, setEditing] = useState<Product | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!authenticated) router.replace("/login");
  }, [authenticated, router]);

  useEffect(() => {
    if (authenticated && businesses.data?.length === 0) router.replace("/onboarding/business");
  }, [authenticated, businesses.data, router]);

  function remove(product: Product) {
    if (window.confirm(`Xóa sản phẩm “${product.name}”?`)) {
      deleteMutation.mutate(product.id, {
        onSuccess: () => { if (editing?.id === product.id) setEditing(null); },
      });
    }
  }

  const filteredProducts = products.data?.filter((p) => {
    if (!search.trim()) return true;
    const query = search.toLowerCase();
    return p.name.toLowerCase().includes(query) || (p.sku && p.sku.toLowerCase().includes(query));
  });

  if (!authenticated || businesses.isLoading) return <Status message="Đang tải doanh nghiệp..." />;
  if (businesses.isError) return <Status message="Không thể tải doanh nghiệp." />;
  if (!business) return <Status message="Đang chuyển đến bước thiết lập..." />;

  return (
    <AppShell businessId={business.id} businessName={business.name} businesses={businesses.data ?? []}>
      <div>
        <p className="text-sm font-bold uppercase tracking-[0.16em] text-green-700">Danh mục</p>
        <h1 className="mt-2 text-3xl font-bold sm:text-4xl">Sản phẩm</h1>
        <p className="mt-3 text-[var(--muted)]">Quản lý giá bán và giá vốn bằng số nguyên VND.</p>

        <Card className="mt-8 p-5 sm:p-7">
          <h2 className="mb-5 text-xl font-bold">{editing ? `Chỉnh sửa ${editing.name}` : "Thêm sản phẩm"}</h2>
          <ProductForm key={editing?.id ?? "new"} businessId={business.id} product={editing} onDone={() => setEditing(null)} />
        </Card>

        <section className="mt-8">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
            <h2 className="text-xl font-bold">Danh sách sản phẩm</h2>
            <div className="flex items-center gap-3">
              <input
                type="text"
                placeholder="Tìm theo tên hoặc SKU..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="rounded-xl border border-[var(--border)] px-3 py-1.5 text-sm outline-none focus:border-green-700"
              />
              {filteredProducts && <span className="text-sm text-[var(--muted)]">{filteredProducts.length} sản phẩm</span>}
            </div>
          </div>
          {products.isLoading && <Card className="p-8 text-center text-[var(--muted)]">Đang tải sản phẩm...</Card>}
          {products.isError && <Card className="p-8 text-center text-red-700">Không thể tải sản phẩm. Vui lòng thử lại.</Card>}
          {products.data?.length === 0 && <Card className="p-8 text-center"><p className="font-semibold">Chưa có sản phẩm</p><p className="mt-2 text-sm text-[var(--muted)]">Thêm sản phẩm đầu tiên bằng biểu mẫu phía trên.</p></Card>}
          {filteredProducts && filteredProducts.length > 0 && (
            <div className="grid gap-3">
              {filteredProducts.map((product) => (
                <Card key={product.id} className="grid gap-4 p-5 sm:grid-cols-[1fr_auto_auto] sm:items-center">
                  <div><div className="flex flex-wrap items-center gap-2"><h3 className="font-bold">{product.name}</h3><span className={`rounded-full px-2 py-1 text-xs font-semibold ${product.is_active ? "bg-green-50 text-green-700" : "bg-stone-100 text-stone-600"}`}>{product.is_active ? "Đang bán" : "Tạm ẩn"}</span></div><p className="mt-1 text-sm text-[var(--muted)]">SKU: {product.sku ?? "—"}</p></div>
                  <div className="grid grid-cols-2 gap-5 text-sm sm:text-right"><div><p className="text-[var(--muted)]">Giá bán</p><p className="mt-1 font-bold">{moneyFormatter.format(product.selling_price)}</p></div><div><p className="text-[var(--muted)]">Giá vốn</p><p className="mt-1 font-bold">{moneyFormatter.format(product.cost_price)}</p></div></div>
                  <div className="flex gap-2 sm:justify-end"><Button className="h-9 bg-white px-3 text-green-800 ring-1 ring-green-800 hover:bg-green-50" onClick={() => setEditing(product)}>Sửa</Button><Button className="h-9 bg-white px-3 text-red-700 ring-1 ring-red-200 hover:bg-red-50" disabled={deleteMutation.isPending} onClick={() => remove(product)}>Xóa</Button></div>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}

function Status({ message }: { message: string }) {
  return <main className="flex min-h-screen items-center justify-center p-6 text-center text-[var(--muted)]">{message}</main>;
}
