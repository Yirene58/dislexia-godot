import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, UserRound, Swords, Star, Mail } from "lucide-react";

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
    <main className="characters-page">
      <header className="characters-header">
        <h1>DISLEXIA GODOT</h1>

        <button onClick={() => navigate("/characters")}>
          <ArrowLeft size={18} />
          Mis personajes
        </button>
      </header>

      <section className="profile-container">
        <div className="profile-heading">
          <UserRound size={52} />
          <div>
            <h2>Mi perfil de aventurero</h2>
            <p>Consulta tus datos y el progreso de tus héroes.</p>
          </div>
        </div>

        <div className="profile-user">
          <h3>{user?.username ?? "Jugador"}</h3>
          <p>
            <Mail size={17} />
            {user?.email ?? "Correo no disponible"}
          </p>
        </div>

        {loading && <p>Cargando estadísticas...</p>}
        {error && <p role="alert">{error}</p>}

        {!loading && !error && (
          <>
            <div className="profile-stats">
              <article className="profile-stat">
                <Swords size={30} />
                <strong>{characters.length}</strong>
                <span>Héroes creados</span>
              </article>

              <article className="profile-stat">
                <Star size={30} />
                <strong>{highestLevel}</strong>
                <span>Nivel más alto</span>
              </article>

              <article className="profile-stat">
                <Star size={30} />
                <strong>{totalExperience}</strong>
                <span>Experiencia total</span>
              </article>
            </div>

            <h3>Mis héroes</h3>

            {characters.length === 0 ? (
              <p>Todavía no tienes héroes creados.</p>
            ) : (
              <div className="profile-heroes">
                {characters.map((character) => (
                  <button
                    key={character.id}
                    className="profile-hero"
                    onClick={() => navigate(`/game/${character.id}`)}
                  >
                    <strong>{character.name}</strong>
                    <span>
                      Nivel {character.level} · {character.experience} XP
                    </span>
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </section>
    </main>
  );
}
