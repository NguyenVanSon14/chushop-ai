const TOKEN_KEY = "chushop_access_token";
const TOKEN_EVENT = "chushop-token-change";

export function getAccessToken(): string | null {
  return typeof window === "undefined" ? null : window.localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.dispatchEvent(new Event(TOKEN_EVENT));
}

export function clearAccessToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
  window.dispatchEvent(new Event(TOKEN_EVENT));
}

export function subscribeToToken(callback: () => void): () => void {
  window.addEventListener("storage", callback);
  window.addEventListener(TOKEN_EVENT, callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener(TOKEN_EVENT, callback);
  };
}
