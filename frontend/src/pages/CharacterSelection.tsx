import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, LogOut, LockKeyhole } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import "../styles/characters.css";
import "../styles/character-selection.css";

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
  const { user, logout } = useAuth();

  const [selectedHero, setSelectedHero] = useState<string>("mushroom");

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

    </main>
  );
}
