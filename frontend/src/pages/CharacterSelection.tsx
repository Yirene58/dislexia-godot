import { Link } from "react-router-dom";
import "../styles/auth.css";

export default function CharacterSelection() {
  return (
    <main className="auth-page">
      <section className="auth-panel">
        <h1>Selección de personajes</h1>
        <p className="auth-subtitle">
          Próximamente podrás crear tu héroe RPG.
        </p>

        <Link to="/login">Volver al login</Link>
      </section>
    </main>
  );
}