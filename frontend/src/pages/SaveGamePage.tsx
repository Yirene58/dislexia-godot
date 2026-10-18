import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Save,
  Trash2,
  MapPin,
  Clock,
  Shield,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import { characterService } from "../services/character.service";
import { saveService } from "../services/save.service";

import type { Character } from "../types/character.types";
import type { SaveGame } from "../types/save.types";

import "../styles/characters.css";
import "../styles/save-game.css";

export default function SaveGamePage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();

  const characterId = Number(id);
  const validId = Number.isSafeInteger(characterId) && characterId > 0;

  const [character, setCharacter] = useState<Character | null>(null);
  const [save, setSave] = useState<SaveGame | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (!token || !validId) {
      setError("No se pudo identificar al personaje.");
      setLoading(false);
      return;
    }

    let active = true;

    Promise.all([
      characterService.getById(token, characterId),
      saveService.get(token, characterId),
    ])
      .then(([characterData, saveData]) => {
        if (!active) return;
        setCharacter(characterData);
        setSave(saveData);
      })
      .catch(() => {
        if (active) {
          setError("No se pudo consultar la partida.");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [token, characterId, validId]);

  const handleSave = async () => {
    if (!token || !validId || saving) return;

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const result = await saveService.save(token, characterId, {
        world_id: "mundo_prueba",
        checkpoint_id: "checkpoint_01",
        status: "in_progress",
        progress_data: {
          source: "web_test",
        },
      });

      setSave(result);
      setMessage("Partida de prueba guardada correctamente.");
    } catch {
      setError("No se pudo guardar la partida.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!token || !validId || saving) return;

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await saveService.delete(token, characterId);
      setSave(null);
      setConfirmDelete(false);
      setMessage("Partida eliminada correctamente.");
    } catch {
      setError("No se pudo eliminar la partida.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="characters-page">
      <header className="characters-header">
        <h1>DISLEXIA GODOT</h1>

        <button onClick={() => navigate("/characters")}>
          <ArrowLeft size={18} />
          Mis personajes
        </button>
      </header>

      <section className="save-container">
        <h2>Partida guardada</h2>

        {loading && <p>Cargando información...</p>}

        {error && <p role="alert" className="save-error">{error}</p>}
        {message && <p role="status" className="save-success">{message}</p>}

        {!loading && character && (
          <>
            <div className="save-character">
              <Shield size={42} />
              <div>
                <h3>{character.name}</h3>
                <p>
                  Nivel {character.level} · {character.experience} XP
                </p>
              </div>
            </div>

            {save ? (
              <div className="save-card">
                <div className="save-info">
                  <MapPin size={24} />
                  <div>
                    <span>Mundo actual</span>
                    <strong>{save.world_id}</strong>
                  </div>
                </div>

                <div className="save-info">
                  <Save size={24} />
                  <div>
                    <span>Punto de guardado</span>
                    <strong>{save.checkpoint_id || "Sin checkpoint"}</strong>
                  </div>
                </div>

                <div className="save-info">
                  <Clock size={24} />
                  <div>
                    <span>Última actualización</span>
                    <strong>
                      {save.updated_at
                        ? new Date(save.updated_at).toLocaleString("es-CO")
                        : "No disponible"}
                    </strong>
                  </div>
                </div>

                <p>
                  Estado: {save.status === "completed"
                    ? "Completada"
                    : "En progreso"}
                </p>

                {confirmDelete ? (
                  <div className="save-actions">
                    <p>¿Eliminar el progreso guardado de este héroe?</p>
                    <button disabled={saving} onClick={handleDelete}>
                      Confirmar eliminación
                    </button>
                    <button
                      disabled={saving}
                      onClick={() => setConfirmDelete(false)}
                    >
                      Cancelar
                    </button>
                  </div>
                ) : (
                  <div className="save-actions">
                    <button
                      disabled={saving}
                      onClick={() => setConfirmDelete(true)}
                    >
                      <Trash2 size={17} />
                      Eliminar partida
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="save-card">
                <h3>No hay partida guardada</h3>
                <p>
                  Este personaje todavía no tiene progreso registrado.
                </p>
              </div>
            )}

            <div className="save-actions">
              <button
                disabled={saving || Boolean(save)}
                onClick={handleSave}
              >
                <Save size={18} />
                {saving ? "Guardando..." : "Crear partida de prueba"}
              </button>
            </div>

            <p className="save-note">
              Esta pantalla permite probar SQLite.
              El progreso real se enviará desde Godot.
            </p>
          </>
        )}
      </section>
    </main>
  );
}
