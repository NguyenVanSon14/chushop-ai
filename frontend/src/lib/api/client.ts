import { clearAccessToken, getAccessToken } from "@/lib/auth/token-storage";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init, headers });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    if (response.status === 401) clearAccessToken();
    throw new ApiError(response.status, payload?.detail ?? "Không thể kết nối đến máy chủ");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
