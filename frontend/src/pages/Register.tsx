import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Eye,
  EyeOff,
  Gamepad2,
  LockKeyhole,
  Mail,
  UserRound,
  UserRoundPlus,
} from "lucide-react";
import { authService } from "../services/auth.service";
import "../styles/paper-login.css";

export default function Register() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
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
      await authService.register({ username, email, password });
      navigate("/login");
    } catch {
      setError("No se pudo registrar. Revisa tus datos e inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="paper-login-page register-page">
      <img className="paper-background-image" src="/images/dislexia-adventure-background.png" alt="" />

      <header className="paper-header">
        <nav className="paper-nav" aria-label="Autenticación">
          <Link className="paper-nav-link" to="/login"><Gamepad2 size={21} /> INICIAR SESIÓN</Link>
          <Link className="paper-nav-link is-current" to="/register" aria-current="page"><UserRoundPlus size={21} /> REGISTRO</Link>
        </nav>
        <Link className="paper-logo" to="/login" aria-label="Dislexia Godot, inicio">
          <span className="logo-dislexia">DISLEXIA</span><span className="logo-godot">GODOT</span>
          <i className="logo-star star-one" aria-hidden="true">✦</i><i className="logo-star star-two" aria-hidden="true">✦</i>
        </Link>
        <span className="paper-header-spacer" aria-hidden="true" />
      </header>

      <section className="register-stage" aria-labelledby="register-title">
        <form className="welcome-card register-card" onSubmit={handleSubmit}>
          <h1 id="register-title">¡Crea tu cuenta!</h1>
          <p className="welcome-subtitle">Únete a la aventura y empieza a aprender a tu ritmo</p>

          <div className="register-field">
            <label htmlFor="register-username"><UserRound size={20} /> NOMBRE DE USUARIO</label>
            <input
              id="register-username"
              type="text"
              autoComplete="username"
              placeholder="Escribe tu nombre de usuario"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </div>

          <div className="register-field">
            <label htmlFor="register-email"><Mail size={20} /> CORREO ELECTRÓNICO</label>
            <input
              id="register-email"
              type="email"
              autoComplete="email"
              placeholder="tucorreo@ejemplo.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="register-field">
            <label htmlFor="register-password"><LockKeyhole size={20} /> CONTRASEÑA</label>
            <div className="register-password-wrap">
              <input
                id="register-password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="Crea una contraseña"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={8}
                required
              />
              <button
                className="register-password-toggle"
                type="button"
                onClick={() => setShowPassword((visible) => !visible)}
                aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            <span className="register-hint">Usa al menos 8 caracteres.</span>
          </div>

          <div className="register-field">
            <label htmlFor="register-confirm-password"><LockKeyhole size={20} /> CONFIRMA TU CONTRASEÑA</label>
            <div className="register-password-wrap">
              <input
                id="register-confirm-password"
                type={showConfirmPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="Repite tu contraseña"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
              <button
                className="register-password-toggle"
                type="button"
                onClick={() => setShowConfirmPassword((visible) => !visible)}
                aria-label={showConfirmPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {error && <p className="login-error" role="alert">{error}</p>}

          <button className="login-submit register-submit" type="submit" disabled={loading}>
            <UserRoundPlus size={23} />
            {loading ? "CREANDO CUENTA..." : "CREAR MI CUENTA"}
          </button>

          <p className="login-register-prompt">¿Ya tienes una cuenta? <Link to="/login">Inicia sesión aquí <span aria-hidden="true">→</span></Link></p>
        </form>
      </section>
    </main>
  );
}
