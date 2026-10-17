const API_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:5000/api").replace(/\/$/, "");

type Credentials = { identifier: string; password: string };
type Registration = { username: string; email: string; password: string };
export type User = { id: number; username: string; email: string };

async function request<T>(path: string, body: object): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`La solicitud falló (${response.status})`);
  return response.json() as Promise<T>;
}

export const authService = {
  register(data: Registration) {
    return request<{ message: string; user: User }>("/auth/register", data);
  },
  login(data: Credentials) {
    return request<{ message: string; access_token: string; user: User }>("/auth/login", data);
  },
};
