import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authService } from "../services/auth.service";
import "../styles/auth.css";

export default function Register() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (password.length < 8) {
      setError("La contraseña debe tener mínimo 8 caracteres.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    setLoading(true);

    try {
      await authService.register({
        username,
        email,
        password,
      });

      navigate("/login");
    } catch {
      setError("No se pudo registrar. Verifica tus datos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-panel">
        <h1>DISLEXIA GODOT</h1>
        <p className="auth-subtitle">Únete a la aventura</p>

        <div className="auth-divider" />

        <h2>Crear cuenta</h2>

        <form onSubmit={handleSubmit}>
          <label>Nombre de usuario</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Nombre de aventurero"
            required
          />

          <label>Correo electrónico</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="correo@ejemplo.com"
            required
          />

          <label>Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />

          <label>Confirmar contraseña</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />

          {error && <p className="auth-error">{error}</p>}

          <button className="auth-submit" disabled={loading}>
            {loading ? "Registrando..." : "Crear cuenta"}
          </button>
        </form>

        <p className="auth-footer">
          ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
        </p>
      </div>
    </main>
  );
}