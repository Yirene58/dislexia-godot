import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { characterService } from "../services/character.service";
import type { Character } from "../types/character.types";

import "../styles/characters.css";
import "../styles/profile.css";

export default function Profile() {
  const navigate = useNavigate();
  const { user, token } = useAuth();

  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let active = true;

    characterService
      .getAll(token)
      .then((data) => {
        if (active) setCharacters(data);
      })
      .catch(() => {
        if (active) setError("No se pudo cargar el perfil.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [token]);

  const highestLevel = characters.reduce(
    (max, character) => Math.max(max, character.level),
    0
  );

  const totalExperience = characters.reduce(
    (total, character) => total + character.experience,
    0
  );

  return (
    <main className="profile-page">
      <div className="profile-scene">
        <header className="profile-scene-header">
          <h1>DISLEXIA GODOT</h1>
          <button onClick={() => navigate("/characters")}>
            Mis personajes
          </button>
        </header>

        <section className="profile-container" aria-label="Perfil de aventurero">
          <h2 className="profile-title">Mi perfil de aventurero</h2>
          <p className="profile-subtitle">
            Consulta tus datos y el progreso de tus héroes.
          </p>

          <div className="profile-avatar">
            <img src="/images/hero-mushroom-cutout.png" alt="Hongo aventurero" />
          </div>

          <div className="profile-user">
            <h3>{user?.username ?? "Jugador"}</h3>
            <p>{user?.email ?? "Correo no disponible"}</p>
          </div>

          {loading && <p className="profile-feedback">Cargando progreso...</p>}
          {error && <p className="profile-feedback" role="alert">{error}</p>}

          {!loading && !error && (
            <div className="profile-stats">
              <article className="profile-stat">
                <strong>{characters.length}</strong>
                <span>Héroes creados</span>
              </article>
              <article className="profile-stat">
                <strong>{highestLevel}</strong>
                <span>Nivel más alto</span>
              </article>
              <article className="profile-stat">
                <strong>{totalExperience}</strong>
                <span>Experiencia total</span>
              </article>
            </div>
          )}

        </section>
      </div>
    </main>
  );
}
