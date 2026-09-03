import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Email không hợp lệ"),
  password: z.string().min(1, "Vui lòng nhập mật khẩu"),
});

export const registerSchema = loginSchema.extend({
  full_name: z.string().trim().min(1, "Vui lòng nhập họ tên").max(255),
  password: z.string().min(8, "Mật khẩu cần ít nhất 8 ký tự").max(128),
});
