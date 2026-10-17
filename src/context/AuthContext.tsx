import {
  createContext,
  useContext,
  useState,
  type ReactNode,
} from "react";

import { authService } from "../services";
import type {
  User,
  LoginRequest,
  AuthContextType,
} from "../types";

type AuthProviderProps = {
  children: ReactNode;
};

type AuthContextValue = AuthContextType & {
  token: string | null;
};

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const login = async (credentials: LoginRequest) => {
    const response = await authService.login(credentials);

    setToken(response.access_token);
    setUser(response.user);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
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
    throw new Error("useAuth debe utilizarse dentro de AuthProvider");
  }

  return context;
}