import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import { authService } from "../services/auth.service";

import type {
  User,
  LoginRequest,
} from "../types/auth.types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const login = async (credentials: LoginRequest) => {
    const response = await authService.login(credentials);

    setUser(response.user);
    setToken(response.access_token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: Boolean(user && token),
        loading: false,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth debe utilizarse dentro de AuthProvider"
    );
  }

  return context;
}
