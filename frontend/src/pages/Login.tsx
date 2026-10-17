import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Shield, Swords } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import "../styles/auth.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login({
        identifier,
        password,
      });

      // Temporal: la gestión segura de sesión se
      // implementará con AuthContext y cookies HttpOnly.
      navigate("/characters");
    } catch {
      setError("Usuario o contraseña incorrectos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-panel">
        <div className="auth-emblem">
          <Swords size={38} />
        </div>

        <h1>DISLEXIA GODOT</h1>
        <p className="auth-subtitle">
          Tu aventura comienza aquí
        </p>

        <div className="auth-divider" />

        <h2>Iniciar sesión</h2>

        <form onSubmit={handleSubmit}>
          <label>Nombre de usuario o correo</label>
          <input
            type="text"
            placeholder="Ingresa tu usuario"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            required
          />

          <label>Contraseña</label>

          <div className="password-field">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Ingresa tu contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
            >
              {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
            </button>
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button
            className="auth-submit"
            type="submit"
            disabled={loading}
          >
            <Shield size={18} />
            {loading ? "Ingresando..." : "Entrar al reino"}
          </button>
        </form>

        <p className="auth-footer">
          ¿Aún no tienes una cuenta?{" "}
          <Link to="/register">Crear personaje</Link>
        </p>
      </div>
    </main>
  );
}
