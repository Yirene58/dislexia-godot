const TOKEN_KEY = "dislexia_access_token";

export const sessionService = {
  getToken(): string | null {
    try {
      return sessionStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },

  setToken(token: string): void {
    sessionStorage.setItem(TOKEN_KEY, token);
  },

  clear(): void {
    sessionStorage.removeItem(TOKEN_KEY);
  },
};
