import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, LogOut, Sword } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { characterService } from "../services/character.service";

import type { Character } from "../types/character.types";

import "../styles/characters.css";

export default function CharacterSelection() {
  const navigate = useNavigate();

  const { user, token, logout } = useAuth();

  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let active = true;

    const loadCharacters = async () => {
      try {
        const data = await characterService.getAll(token);

        if (active) {
          setCharacters(data);
        }
      } catch {
        if (active) {
          setError("No se pudieron cargar los personajes.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadCharacters();

    return () => {
      active = false;
    };
  }, [token]);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <main className="characters-page">
      <header className="characters-header">
        <div>
          <h1>DISLEXIA GODOT</h1>
          <p>Bienvenido, {user?.username}</p>
        </div>

        <button onClick={handleLogout}>
          <LogOut size={18} />
          Cerrar sesión
        </button>
      </header>

      <section className="characters-container">
        <h2>Selecciona tu personaje</h2>

        <p className="characters-description">
          Elige un héroe para continuar tu aventura.
        </p>

        {loading && <p>Cargando personajes...</p>}

        {error && <p role="alert">{error}</p>}

        {!loading && !error && (
          <div className="characters-grid">
            {characters.map((character) => (
              <article
                key={character.id}
                className="character-card"
              >
                <div className="character-avatar">
                  <Sword size={56} />
                </div>

                <h3>{character.name}</h3>

                <p>
                  Clase: {character.character_class}
                </p>

                <p>Nivel: {character.level}</p>

                <button
                  onClick={() =>
                    navigate(`/game/${character.id}`)
                  }
                >
                  Seleccionar personaje
                </button>
              </article>
            ))}

            <article className="character-card create-card">
              <Plus size={55} />

              <h3>Nuevo personaje</h3>

              <p>Crea un héroe para tu aventura.</p>

              <button
                onClick={() => navigate("/characters/create")}
              >
                Crear personaje
              </button>
            </article>
          </div>
        )}
      </section>
    </main>
  );
}