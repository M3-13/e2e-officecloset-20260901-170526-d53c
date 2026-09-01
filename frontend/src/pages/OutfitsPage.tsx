import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { apiErrorMessage } from "../api/client";
import * as outfitsApi from "../api/outfits";
import type { ClothingItem, Outfit } from "../api/types";
import { useAuth } from "../auth/AuthContext";

const CATEGORY_LABELS: Record<ClothingItem["category"], string> = {
  top: "Oberteil",
  bottom: "Unterteil",
  shoes: "Schuhe",
  accessory: "Accessoire",
};

function ItemPreview({ item }: { item: ClothingItem }) {
  return (
    <div
      style={{
        background: "#1f1822",
        border: "1px solid #332b30",
        borderRadius: 16,
        padding: 16,
        minHeight: 220,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
      }}
    >
      {item.image_url ? (
        <img
          src={item.image_url}
          alt={item.name}
          style={{
            width: "100%",
            maxHeight: 180,
            objectFit: "cover",
            borderRadius: 8,
          }}
          onError={(event) => {
            (event.currentTarget as HTMLImageElement).style.display = "none";
          }}
        />
      ) : (
        <div
          style={{
            width: "100%",
            height: 140,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "#17121a",
            borderRadius: 8,
            color: "#c9a24b",
            fontSize: 36,
          }}
        >
          {item.name.slice(0, 1)}
        </div>
      )}
      <div style={{ textAlign: "center" }}>
        <div style={{ fontWeight: 600 }}>{item.name}</div>
        <div style={{ color: "#a99c8e", fontSize: 12 }}>
          {CATEGORY_LABELS[item.category]}
        </div>
      </div>
    </div>
  );
}

export default function OutfitsPage() {
  const { isAuthenticated } = useAuth();

  const [items, setItems] = useState<ClothingItem[]>([]);
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [name, setName] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [loadedItems, loadedOutfits] = await Promise.all([
        outfitsApi.listItems(),
        outfitsApi.list(),
      ]);
      setItems(loadedItems);
      setOutfits(loadedOutfits);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      void load();
    }
  }, [isAuthenticated, load]);

  const selectedItems = useMemo(
    () => items.filter((item) => selectedIds.includes(item.id)),
    [items, selectedIds],
  );

  function toggleItem(itemId: number) {
    setSelectedIds((current) =>
      current.includes(itemId)
        ? current.filter((id) => id !== itemId)
        : [...current, itemId],
    );
  }

  function resetForm() {
    setName("");
    setSelectedIds([]);
    setEditingId(null);
  }

  async function handleSave() {
    const trimmed = name.trim();
    if (!trimmed) {
      setError("Bitte gib deinem Outfit einen Namen.");
      return;
    }
    setError(null);
    try {
      if (editingId !== null) {
        await outfitsApi.update(editingId, { name: trimmed, item_ids: selectedIds });
      } else {
        await outfitsApi.create(trimmed, selectedIds);
      }
      resetForm();
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  function handleOpen(outfit: Outfit) {
    setEditingId(outfit.id);
    setName(outfit.name);
    setSelectedIds(outfit.items.map((item) => item.id));
  }

  async function handleDelete(outfit: Outfit) {
    if (!window.confirm(`Outfit „${outfit.name}“ wirklich löschen?`)) {
      return;
    }
    setError(null);
    try {
      await outfitsApi.remove(outfit.id);
      if (editingId === outfit.id) {
        resetForm();
      }
      await load();
    } catch (err) {
      setError(apiErrorMessage(err));
    }
  }

  if (!isAuthenticated) {
    return (
      <section className="container page">
        <div className="empty-state">
          <h2>Bitte anmelden</h2>
          <p>Melde dich an, um deine Outfits zu erstellen und zu verwalten.</p>
          <Link className="btn btn-primary" to="/login">
            Zur Anmeldung
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="container page">
      <h1 className="page-title">Outfit-Creator</h1>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr",
          gap: 32,
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <h2>Vorschau</h2>
          {selectedItems.length === 0 ? (
            <div
              style={{
                background: "#1f1822",
                border: "1px dashed #332b30",
                borderRadius: 16,
                padding: 32,
                minHeight: 220,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                textAlign: "center",
                color: "#a99c8e",
              }}
            >
              Wähle Teile aus deiner Garderobe, um dein Outfit zu kombinieren.
            </div>
          ) : (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr",
                gap: 16,
              }}
            >
              {selectedItems.map((item) => (
                <ItemPreview key={item.id} item={item} />
              ))}
            </div>
          )}

          <h2>Teile auswählen</h2>
          {loading && items.length === 0 ? (
            <p className="text-muted">Lade Garderobe …</p>
          ) : items.length === 0 ? (
            <div className="empty-state">
              <h2>Noch keine Teile</h2>
              <p>Lege zuerst Kleidungsstücke in deiner Garderobe an.</p>
              <Link className="btn btn-secondary" to="/wardrobe">
                Zur Garderobe
              </Link>
            </div>
          ) : (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {items.map((item) => {
                const active = selectedIds.includes(item.id);
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => toggleItem(item.id)}
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 8,
                      minHeight: 44,
                      padding: "8px 16px",
                      border: `1px solid ${active ? "#c9a24b" : "#332b30"}`,
                      borderRadius: 999,
                      background: active ? "#c9a24b" : "transparent",
                      color: active ? "#1a1410" : "#a99c8e",
                      fontWeight: active ? 600 : 400,
                      cursor: "pointer",
                      fontSize: 14,
                    }}
                  >
                    <span style={{ fontSize: 12, opacity: 0.8 }}>
                      {CATEGORY_LABELS[item.category]}
                    </span>
                    <span>{item.name}</span>
                  </button>
                );
              })}
            </div>
          )}

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 16,
              marginTop: 16,
            }}
          >
            <label className="text-muted" htmlFor="outfit-name">
              Name des Outfits
            </label>
            <input
              id="outfit-name"
              className="input"
              type="text"
              value={name}
              maxLength={120}
              placeholder="z. B. Red-Carpet-Abend"
              onChange={(event) => setName(event.target.value)}
            />
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
              <button
                type="button"
                className="btn btn-primary"
                disabled={!name.trim() || selectedItems.length === 0}
                onClick={() => void handleSave()}
              >
                {editingId !== null ? "Änderungen speichern" : "Outfit speichern"}
              </button>
              {editingId !== null && (
                <button type="button" className="btn btn-secondary" onClick={resetForm}>
                  Abbrechen
                </button>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <h2>Meine Outfits</h2>
          {loading && outfits.length === 0 ? (
            <p className="text-muted">Lade Outfits …</p>
          ) : outfits.length === 0 ? (
            <p className="text-muted">Noch keine gespeicherten Outfits.</p>
          ) : (
            <ul
              style={{
                listStyle: "none",
                margin: 0,
                padding: 0,
                display: "flex",
                flexDirection: "column",
                gap: 16,
              }}
            >
              {outfits.map((outfit) => (
                <li
                  key={outfit.id}
                  style={{
                    background: "#17121a",
                    border: "1px solid #332b30",
                    borderRadius: 16,
                    padding: 16,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: 8,
                    }}
                  >
                    <span style={{ fontWeight: 600 }}>{outfit.name}</span>
                    <span style={{ color: "#a99c8e", fontSize: 14 }}>
                      {outfit.items.length} Teile
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => handleOpen(outfit)}
                    >
                      Bearbeiten
                    </button>
                    <button
                      type="button"
                      className="btn btn-danger"
                      onClick={() => void handleDelete(outfit)}
                    >
                      Löschen
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
