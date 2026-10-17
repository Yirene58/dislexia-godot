export interface User {
  id: number;
  username: string;
  email?: string;
}

export interface LoginRequest {
  identifier: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}