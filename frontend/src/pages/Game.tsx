import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Shield, Star, Swords } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { characterService } from "../services/character.service";

import type { Character } from "../types/character.types";

import "../styles/characters.css";

export default function Game() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();

  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token || !id || !Number.isSafeInteger(Number(id)) || Number(id) <= 0) {
      setError("Personaje no válido.");
      setLoading(false);
      return;
    }

    let active = true;

    characterService
      .getById(token, Number(id))
      .then((data) => {
        if (active) setCharacter(data);
      })
      .catch(() => {
        if (active) setError("No se pudo cargar el personaje.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [id, token]);

  const classNames: Record<string, string> = {
    warrior: "Guerrero",
    mage: "Mago",
    archer: "Arquero",
  };

  return (
    <main className="characters-page">
      <header className="characters-header">
        <h1>DISLEXIA GODOT</h1>

        <button onClick={() => navigate("/characters")}>
          <ArrowLeft size={18} />
          Volver
        </button>
      </header>

      <section className="characters-container">
        <button
          disabled={!character}
          onClick={() => navigate(`/characters/${character?.id}/save`)}
        >
          Ver partida guardada
        </button>
        {loading && <p>Cargando personaje...</p>}

        {error && <p role="alert">{error}</p>}

        {!loading && character && (
          <>
            <h2>{character.name}</h2>
            <p className="characters-description">
              Tu héroe está listo para la aventura.
            </p>

            <div className="characters-grid">
              <article className="character-card">
                <Swords size={60} color="#e7c77e" />
                <h3>Clase</h3>
                <p>
                  {classNames[character.character_class] ??
                    character.character_class}
                </p>
              </article>

              <article className="character-card">
                <Shield size={60} color="#e7c77e" />
                <h3>Nivel</h3>
                <p>{character.level}</p>
              </article>

              <article className="character-card">
                <Star size={60} color="#e7c77e" />
                <h3>Experiencia</h3>
                <p>{character.experience} XP</p>
              </article>
            </div>

            <p className="characters-description" style={{ marginTop: 36 }}>
              Próximamente podrás iniciar tu aventura en Godot.
            </p>
          </>
        )}
      </section>
    </main>
  );
}

