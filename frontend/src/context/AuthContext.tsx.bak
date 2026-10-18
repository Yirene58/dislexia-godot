import { createContext, useContext, useState, type ReactNode } from "react";
import { authService, type User } from "../services/auth.service";

type AuthContextValue = {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: { identifier: string; password: string }) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login: AuthContextValue["login"] = async (credentials) => {
    const response = await authService.login(credentials);
    setUser(response.user);
  };

  const logout = () => setUser(null);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: user !== null, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth debe utilizarse dentro de AuthProvider");
  return context;
}
