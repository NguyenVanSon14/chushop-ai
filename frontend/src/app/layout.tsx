import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/providers/query-provider";

export const metadata: Metadata = {
  title: "ChủShop AI",
  description: "Money Brain cho chủ shop Việt",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="vi">
      <body><QueryProvider>{children}</QueryProvider></body>
    </html>
  );
}
