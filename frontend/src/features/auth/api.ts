import { apiRequest } from "@/lib/api/client";
import type { TokenResponse, User } from "@/lib/api/types";

export type RegisterInput = { email: string; password: string; full_name: string };
export type LoginInput = { email: string; password: string };

export const register = (input: RegisterInput) =>
  apiRequest<User>("/auth/register", { method: "POST", body: JSON.stringify(input) });

export const login = (input: LoginInput) =>
  apiRequest<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify(input) });

export const getMe = () => apiRequest<User>("/auth/me");
