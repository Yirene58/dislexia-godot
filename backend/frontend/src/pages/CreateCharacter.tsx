import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { characterService } from "../services/character.service";

import type { CharacterClass } from "../types/character.types";

import "../styles/auth.css";

export default function CreateCharacter() {
  const navigate = useNavigate();
  const { token } = useAuth();

  const [name, setName] = useState("");
  const [characterClass, setCharacterClass] =
    useState<CharacterClass>("warrior");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

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

      navigate("/characters");
    } catch {
      setError("No se pudo crear el personaje.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-panel">
        <h1>CREAR PERSONAJE</h1>

        <p className="auth-subtitle">
          Un nuevo héroe está por nacer
        </p>

        <div className="auth-divider" />

        <form onSubmit={handleSubmit}>
          <label>Nombre del personaje</label>

          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            minLength={3}
            maxLength={50}
            required
            placeholder="Nombre de tu héroe"
          />

          <label>Selecciona una clase</label>

          <select
            value={characterClass}
            onChange={(e) =>
              setCharacterClass(
                e.target.value as CharacterClass
              )
            }
            style={{
              width: "100%",
              padding: "12px",
              background: "#121711",
              color: "#f4e8c8",
              border: "1px solid #776342",
              borderRadius: "5px",
            }}
          >
            <option value="warrior">Guerrero</option>
            <option value="mage">Mago</option>
            <option value="archer">Arquero</option>
          </select>

          {error && <p className="auth-error">{error}</p>}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? "Creando..." : "Crear héroe"}
          </button>
        </form>

        <button
          type="button"
          className="auth-submit"
          onClick={() => navigate("/characters")}
        >
          Volver
        </button>
      </section>
    </main>
  );
}