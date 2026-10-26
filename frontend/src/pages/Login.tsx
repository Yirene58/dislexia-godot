import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Gamepad2, LockKeyhole, Play, UserRound, UserRoundPlus } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import "../styles/paper-login.css";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login({ identifier, password });
      navigate("/characters");
    } catch {
      setError("Usuario o contraseña incorrectos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="paper-login-page">
      <img className="paper-background-image" src="/images/dislexia-adventure-background.png" alt="" />

      <header className="paper-header">
        <nav className="paper-nav" aria-label="Autenticación">
          <Link className="paper-nav-link is-current" to="/login" aria-current="page"><Gamepad2 size={21} /> INICIAR SESIÓN</Link>
          <Link className="paper-nav-link" to="/register"><UserRoundPlus size={21} /> REGISTRO</Link>
        </nav>
        <Link className="paper-logo" to="/login" aria-label="Dislexia Godot, inicio">
          <span className="logo-dislexia">DISLEXIA</span><span className="logo-godot">GODOT</span>
          <i className="logo-star star-one" aria-hidden="true">✦</i><i className="logo-star star-two" aria-hidden="true">✦</i>
        </Link>
        <span className="paper-header-spacer" aria-hidden="true" />
      </header>

      <section className="login-stage" aria-labelledby="welcome-title">
        <div className="login-masthead">
          <h2 className="wood-plaque">Una aventura para aprender a tu ritmo</h2>
          <p className="learning-motto"><span>LEE</span><b>•</b><span>JUEGA</span><b>•</b><span>DESCUBRE</span><b>•</b><span>APRENDE</span></p>
        </div>

        <form className="welcome-card" onSubmit={handleSubmit}>
          <h1 id="welcome-title">¡Bienvenido/a!</h1>
          <p className="welcome-subtitle">Inicia sesión para continuar tu aventura</p>

          <div className="login-field">
            <label htmlFor="login-username"><UserRound size={22} /> NOMBRE DE USUARIO</label>
            <input
              id="login-username"
              type="text"
              autoComplete="username"
              placeholder="Escribe tu nombre"
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              required
            />
          </div>

          <div className="login-field">
            <label htmlFor="login-password"><LockKeyhole size={22} /> CLAVE SECRETA</label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              placeholder="Tu contraseña"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          {error && <p className="login-error" role="alert">{error}</p>}

          <button className="login-submit" type="submit" disabled={loading}>
            <Play size={29} fill="currentColor" />
            {loading ? "ENTRANDO..." : "ENTRAR A MI AVENTURA"}
          </button>

          <p className="login-register-prompt">¿Aún no tienes cuenta? <Link to="/register">Regístrate aquí <span aria-hidden="true">→</span></Link></p>
        </form>
      </section>
    </main>
  );
}
