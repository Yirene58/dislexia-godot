import { useState, type FormEvent } from "react";
import { ArrowLeft, Check, Save } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { characterService } from "../services/character.service";
import type { CharacterClass } from "../types/character.types";

import "../styles/create-character.css";

const CLASSES: { id: CharacterClass; name: string; icon: string }[] = [
  { id: "mage", name: "Mago", icon: "🪄" },
  { id: "warrior", name: "Guerrero", icon: "⚔️" },
  { id: "archer", name: "Arquero", icon: "🏹" },
];

export default function CreateCharacter() {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [name, setName] = useState("");
  const [characterClass, setCharacterClass] = useState<CharacterClass>("warrior");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!token) {
      setError("Debes iniciar sesión.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      await characterService.create(token, {
        name: name.trim(),
        character_class: characterClass,
      });

      navigate("/profile");
    } catch {
      setError("No se pudo guardar el personaje. Inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mushroom-customizer-page">
      <img className="customizer-background" src="/images/create-character-background.png" alt="" />

      <header className="customizer-header">
        <button className="customizer-back" type="button" onClick={() => navigate("/characters")}>
          <ArrowLeft size={21} /> VOLVER
        </button>
        <div className="customizer-title-wrap">
          <h1>CREA TU PERSONAJE</h1>
          <p>Dale un nombre, elige una clase y prepara tu honguito para comenzar la aventura</p>
        </div>
      </header>

      <div className="customizer-layout">
        <section className="mushroom-preview-panel" aria-label="Vista previa de tu personaje">
          <div className="mushroom-preview-frame">
            <img src="/images/hero-mushroom.png" alt="Vista previa del personaje honguito" />
          </div>
          <p className="preview-caption">Tu honguito aventurero</p>
        </section>

        <form className="customizer-card" onSubmit={handleSubmit}>
          <div className="customizer-name-field">
            <label htmlFor="character-name"><span>👤</span> NOMBRE DEL PERSONAJE</label>
            <input
              id="character-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              minLength={3}
              maxLength={50}
              required
              placeholder="Escribe un nombre para tu honguito"
            />
          </div>

          <fieldset className="customizer-section">
            <legend><span aria-hidden="true">⚔️</span> CLASE</legend>
            <div className="class-choice-grid">
              {CLASSES.map((option) => (
                <button
                  className={`class-choice${characterClass === option.id ? " is-selected" : ""}`}
                  type="button"
                  key={option.id}
                  aria-pressed={characterClass === option.id}
                  onClick={() => setCharacterClass(option.id)}
                >
                  <span>{option.icon}</span>
                  <strong>{option.name}</strong>
                  {characterClass === option.id && <Check className="class-choice-check" size={17} />}
                </button>
              ))}
            </div>
          </fieldset>

          {error && <p className="customizer-error" role="alert">{error}</p>}

          <button className="customizer-submit" type="submit" disabled={loading}>
            <Save size={21} /> {loading ? "GUARDANDO..." : "CREAR PERSONAJE"}
          </button>
        </form>
      </div>
    </main>
  );
}
