import { useNavigate } from "react-router-dom";
import { LogOut, Shield, Swords } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import "../styles/auth.css";

export default function CharacterSelection() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div className="auth-emblem">
          <Swords size={40} />
        </div>

        <h1>DISLEXIA GODOT</h1>

        <p className="auth-subtitle">
          Bienvenido al reino, {user?.username}
        </p>

        <div className="auth-divider" />

        <Shield size={48} color="#d7b86d" />

        <h2>Selección de personajes</h2>

        <p className="auth-subtitle">
          Pronto podrás crear tu personaje,
          seleccionar su clase y comenzar tu aventura.
        </p>

        <button
          className="auth-submit"
          onClick={handleLogout}
        >
          <LogOut size={18} />
          Cerrar sesión
        </button>
      </section>
    </main>
  );
}