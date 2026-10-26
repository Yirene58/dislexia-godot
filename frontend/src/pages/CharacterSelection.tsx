import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, LogOut, LockKeyhole, Plus, Sword, Trash2 } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { characterService } from "../services/character.service";
import type { Character } from "../types/character.types";

import "../styles/characters.css";
import "../styles/character-selection.css";

const CLASS_LABELS: Record<string, string> = {
  warrior: "Guerrero",
  mage: "Mago",
  archer: "Arquero",
};

const HEROES = [
  {
    id: "mushroom",
    name: "HONGUITO",
    image: "/images/hero-mushroom.png",
    description: "Un pequeño explorador del bosque, curioso y valiente.",
    available: true,
  },
  {
    id: "rabbit",
    name: "CONEJO",
    image: "/images/hero-rabbit.png",
    description: "Rápido, ágil y siempre listo para una nueva aventura.",
    available: false,
  },
  {
    id: "fox",
    name: "ZORRO",
    image: "/images/hero-fox.png",
    description: "Inteligente, astuto y un gran guía en el camino.",
    available: false,
  },
] as const;

export default function CharacterSelection() {
  const navigate = useNavigate();
  const { user, token, logout } = useAuth();

  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [selectedHero, setSelectedHero] = useState<string>("mushroom");

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let active = true;

    async function loadCharacters() {
      try {
        const data = await characterService.getAll(token!);

        if (active) {
          setCharacters(data);
        }
      } catch {
        if (active) {
          setError("No se pudieron cargar los personajes guardados.");
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    loadCharacters();

    return () => {
      active = false;
    };
  }, [token]);

  const handleDelete = async (characterId: number) => {
    if (!token) return;

    setDeletingId(characterId);
    setError("");

    try {
      await characterService.delete(token, characterId);

      setCharacters((previous) =>
        previous.filter((character) => character.id !== characterId)
      );

      setConfirmId(null);
    } catch {
      setError("No se pudo eliminar el personaje.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <main className="character-selection-page">
      <img
        className="character-selection-background"
        src="/images/character-selection-background.png"
        alt=""
      />

      <header className="selection-header">
        <p className="selection-welcome">Bienvenido/a, <strong>{user?.username}</strong></p>
        <Link className="selection-logo" to="/characters" aria-label="Dislexia Godot">
          <span>DISLEXIA</span><span>GODOT</span>
        </Link>
        <button className="selection-logout" onClick={handleLogout}>
          <LogOut size={18} /> Cerrar sesión
        </button>
      </header>

      <section className="hero-selection" aria-labelledby="hero-selection-title">
        <h1 className="selection-title" id="hero-selection-title">Selecciona tu personaje</h1>
        <p className="selection-subtitle">Cada héroe tiene una historia única. ¡Elige con quién comenzar tu aventura!</p>

        <div className="hero-choice-grid">
          {HEROES.map((hero) => {
            const isSelected = selectedHero === hero.id;

            return (
              <button
                className={`hero-choice-card${isSelected ? " is-selected" : ""}${!hero.available ? " is-locked" : ""}`}
                type="button"
                key={hero.id}
                disabled={!hero.available}
                aria-pressed={isSelected}
                onClick={() => setSelectedHero(hero.id)}
              >
                <span className="hero-choice-image-wrap">
                  <img className="hero-choice-image" src={hero.image} alt="" />
                  {!hero.available && <span className="hero-locked-badge"><LockKeyhole size={15} /> Próximamente</span>}
                </span>
                <span className="hero-choice-name">{hero.name}</span>
                <span className="hero-choice-description">{hero.description}</span>
              </button>
            );
          })}
        </div>

        <button
          className="continue-hero-button"
          type="button"
          disabled={selectedHero !== "mushroom"}
          onClick={() => navigate("/characters/create")}
        >
          <ArrowRight size={27} fill="currentColor" />
          CONTINUAR CON ESTE PERSONAJE
        </button>
      </section>

      {(loading || error || characters.length > 0) && (
        <section className="saved-characters" aria-labelledby="saved-characters-title">
          <h2 id="saved-characters-title">Tus personajes guardados</h2>
          {loading && <p className="saved-characters-message">Cargando personajes...</p>}
          {error && <p className="saved-characters-error" role="alert">{error}</p>}

          {!loading && !error && (
            <div className="characters-grid">
              {characters.map((character) => (
                <article key={character.id} className="character-card">
                  <div className="character-avatar"><Sword size={56} /></div>
                  <h3>{character.name}</h3>
                  <p>Clase: {CLASS_LABELS[character.character_class] ?? character.character_class}</p>
                  <p>Nivel: {character.level}</p>
                  <p>Experiencia: {character.experience} XP</p>
                  <button onClick={() => navigate(`/game/${character.id}`)}>
                    Seleccionar personaje
                  </button>

                  {confirmId === character.id ? (
                    <div className="delete-confirmation">
                      <p>¿Eliminar este personaje definitivamente?</p>
                      <button disabled={deletingId !== null} onClick={() => handleDelete(character.id)}>
                        {deletingId === character.id ? "Eliminando..." : "Confirmar eliminación"}
                      </button>
                      <button disabled={deletingId !== null} onClick={() => setConfirmId(null)}>Cancelar</button>
                    </div>
                  ) : (
                    <button onClick={() => setConfirmId(character.id)} disabled={deletingId !== null}>
                      <Trash2 size={16} /> Eliminar personaje
                    </button>
                  )}
                </article>
              ))}

              <article className="character-card create-card">
                <Plus size={55} />
                <h3>Nuevo personaje</h3>
                <p>Crea otro héroe para tu aventura.</p>
                <button onClick={() => navigate("/characters/create")}>Crear personaje</button>
              </article>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
