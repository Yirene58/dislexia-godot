import { api } from "./api";

import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  User,
} from "../types";

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>(
      "/auth/login",
      data
    );

    return response.data;
  },

  async register(data: RegisterRequest): Promise<void> {
    await api.post("/auth/register", data);
  },

  async getProfile(token: string): Promise<User> {
    const response = await api.get<User>("/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  },
};