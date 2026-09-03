import { AuthShell } from "@/features/auth/auth-shell";
import { LoginFooter, LoginForm } from "@/features/auth/login-form";

export default function LoginPage() {
  return <AuthShell title="Chào mừng trở lại" subtitle="Đăng nhập để tiếp tục quản lý shop." footer={<LoginFooter />}><LoginForm /></AuthShell>;
}
