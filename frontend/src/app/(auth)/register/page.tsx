import { AuthShell } from "@/features/auth/auth-shell";
import { RegisterFooter, RegisterForm } from "@/features/auth/register-form";

export default function RegisterPage() {
  return <AuthShell title="Bắt đầu với ChủShop" subtitle="Tạo tài khoản để thiết lập doanh nghiệp đầu tiên." footer={<RegisterFooter />}><RegisterForm /></AuthShell>;
}
