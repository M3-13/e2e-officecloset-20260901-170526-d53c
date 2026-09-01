import { useEffect, useRef, useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { apiErrorMessage, getAuthToken } from "../api/client";
import type { Category, ClothingItem } from "../api/types";
import {
  createItem,
  listItems,
  removeItem,
  updateItem,
  type CreateItemInput,
  type UpdateItemInput,
} from "../api/wardrobe";
const WARDROBE_STYLES = `
.page-header { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-4); }
.filter-bar { display: flex; flex-wrap: wrap; gap: var(--space-1); margin-bottom: var(--space-4); }
.chip { display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: var(--space-1) var(--space-3); border-radius: var(--radius-pill); border: 1px solid var(--color-border); background: transparent; color: var(--color-muted); font-family: var(--font-family); font-size: var(--size-sm); cursor: pointer; transition: border-color 150ms, background-color 150ms, color 150ms; }
.chip:hover { border-color: var(--color-accent); }
.chip-active { background: var(--color-accent); border-color: var(--color-accent); color: #1a1410; font-weight: 600; }
.gallery-grid { display: grid; gap: var(--space-3); grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); }
.gallery-item { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35); }
.gallery-image { width: 100%; aspect-ratio: 3 / 4; object-fit: cover; display: block; }
.gallery-placeholder { display: flex; align-items: center; justify-content: center; text-align: center; padding: var(--space-3); color: var(--color-muted); background: var(--color-surface_alt); }
.gallery-body { padding: var(--space-2); display: flex; flex-direction: column; gap: var(--space-1); }
.gallery-title { font-family: var(--heading-font-family); font-weight: 600; font-size: var(--size-md); color: var(--color-fg); margin: 0; }
.gallery-badge { align-self: flex-start; font-size: var(--size-xs); color: var(--color-muted); border: 1px solid var(--color-border); border-radius: var(--radius-pill); padding: 2px var(--space-1); }
.gallery-meta { font-size: var(--size-sm); color: var(--color-muted); }
.gallery-actions { display: flex; gap: var(--space-1); margin-top: var(--space-1); }
.gallery-actions .btn { flex: 1; min-height: 44px; padding: var(--space-1) var(--space-2); font-size: var(--size-sm); }
.modal-overlay { position: fixed; inset: 0; background: rgba(14, 11, 16, 0.72); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; padding: var(--space-3); z-index: 100; }
.modal-panel { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); max-width: 480px; width: 100%; padding: var(--space-4); max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-bottom: var(--space-3); }
.modal-title { font-size: var(--size-lg); margin: 0; }
.modal-close { width: 44px; height: 44px; display: inline-flex; align-items: center; justify-content: center; border: none; border-radius: var(--radius-md); background: transparent; color: var(--color-muted); font-size: var(--size-xl); line-height: 1; cursor: pointer; }
.modal-close:hover { background: var(--color-surface_alt); color: var(--color-fg); }
.form-field { display: flex; flex-direction: column; gap: var(--space-1); margin-bottom: var(--space-3); }
.form-label { font-size: var(--size-sm); color: var(--color-fg); }
.dropzone { display: flex; align-items: center; justify-content: center; border: 2px dashed var(--color-border); border-radius: var(--radius-lg); padding: var(--space-4); min-height: 160px; background: var(--color-surface_alt); cursor: pointer; transition: border-color 150ms, background-color 150ms; }
.dropzone:hover { border-color: var(--color-accent); background: rgba(201, 162, 75, 0.05); }
.dropzone input[type="file"] { display: none; }
.dropzone-hint { color: var(--color-muted); text-align: center; }
.preview-image { width: 100%; max-height: 320px; object-fit: cover; border-radius: var(--radius-md); display: block; }
.modal-actions { display: flex; gap: var(--space-2); margin-top: var(--space-4); }
.modal-actions .btn { flex: 1; }
`;

const CATEGORY_LABELS: Record<Category, string> = {
  top: "Oberteile",
  bottom: "Unterteile",
  shoes: "Schuhe",
  accessory: "Accessoires",
};

const CATEGORIES = Object.keys(CATEGORY_LABELS) as Category[];

type Filter = Category | "all";

interface FormState {
  name: string;
  category: Category;
  color: string;
  brand: string;
  image: File | null;
}

const EMPTY_FORM: FormState = {
  name: "",
  category: "top",
  color: "",
  brand: "",
  image: null,
};

function AuthedImage({
  src,
  alt,
  className = "gallery-image",
}: {
  src: string;
  alt: string;
  className?: string;
}) {
  const [url, setUrl] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let objectUrl: string | null = null;
    const token = getAuthToken();
    if (!token) {
      setFailed(true);
      return;
    }
    setUrl(null);
    setFailed(false);
    fetch(src, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) throw new Error(String(res.status));
        return res.blob();
      })
      .then((blob) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      })
      .catch(() => {
        if (!cancelled) setFailed(true);
      });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [src]);

  if (failed) {
    return <div className={`${className} gallery-placeholder`}>Bild nicht verfügbar</div>;
  }
  if (!url) {
    return <div className={`${className} gallery-placeholder`}>Lade Bild …</div>;
  }
  return <img className={className} src={url} alt={alt} />;
}

export default function WardrobePage() {
  const { isAuthenticated } = useAuth();

  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");
  const [refreshKey, setRefreshKey] = useState(0);

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<ClothingItem | null>(null);
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [deleteTarget, setDeleteTarget] = useState<ClothingItem | null>(null);
  const [deleting, setDeleting] = useState(false);

  const previewUrlRef = useRef<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    listItems(filter === "all" ? undefined : filter)
      .then((data) => {
        if (!cancelled) setItems(data);
      })
      .catch((err) => {
        if (!cancelled) setError(apiErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, filter, refreshKey]);

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, []);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  function selectImage(file: File | null) {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    const url = file ? URL.createObjectURL(file) : null;
    previewUrlRef.current = url;
    setPreviewUrl(url);
    setForm((prev) => ({ ...prev, image: file }));
  }

  function openCreate() {
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setPreviewUrl(null);
    setFormOpen(true);
  }

  function openEdit(item: ClothingItem) {
    setEditing(item);
    setForm({
      name: item.name,
      category: item.category,
      color: item.color ?? "",
      brand: item.brand ?? "",
      image: null,
    });
    setFormError(null);
    setPreviewUrl(null);
    setFormOpen(true);
  }

  function closeForm() {
    if (saving) return;
    setFormOpen(false);
    setEditing(null);
    setForm(EMPTY_FORM);
    setFormError(null);
    setPreviewUrl(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!form.name.trim()) {
      setFormError("Bitte einen Namen eingeben.");
      return;
    }
    setFormError(null);
    setSaving(true);
    try {
      if (editing) {
        const input: UpdateItemInput = {
          name: form.name.trim(),
          category: form.category,
          color: form.color.trim(),
          brand: form.brand.trim(),
        };
        if (form.image) input.image = form.image;
        await updateItem(editing.id, input);
      } else {
        const input: CreateItemInput = {
          name: form.name.trim(),
          category: form.category,
          color: form.color.trim(),
          brand: form.brand.trim(),
        };
        if (form.image) input.image = form.image;
        await createItem(input);
      }
      setFormOpen(false);
      setEditing(null);
      setForm(EMPTY_FORM);
      setPreviewUrl(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      setFormError(apiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await removeItem(deleteTarget.id);
      setDeleteTarget(null);
      setRefreshKey((k) => k + 1);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setDeleting(false);
    }
  }

  return (
    <section className="container page">
      <style>{WARDROBE_STYLES}</style>
      <div className="page-header">
        <h1 className="page-title">Garderobe</h1>
        <button type="button" className="btn btn-primary" onClick={openCreate}>
          Neu anlegen
        </button>
      </div>

      <div className="filter-bar" role="group" aria-label="Kategorie-Filter">
        <button
          type="button"
          className={filter === "all" ? "chip chip-active" : "chip"}
          onClick={() => setFilter("all")}
        >
          Alle
        </button>
        {CATEGORIES.map((category) => (
          <button
            key={category}
            type="button"
            className={filter === category ? "chip chip-active" : "chip"}
            onClick={() => setFilter(category)}
          >
            {CATEGORY_LABELS[category]}
          </button>
        ))}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <p className="text-muted">Lade Garderobe …</p>
      ) : items.length === 0 ? (
        <div className="empty-state">
          <h2>Noch keine Kleidungsstücke</h2>
          <p>Lege dein erstes Kleidungsstück an – mit Bild und Kategorie.</p>
        </div>
      ) : (
        <div className="gallery-grid">
          {items.map((item) => (
            <article className="gallery-item" key={item.id}>
              {item.image_url ? (
                <AuthedImage src={item.image_url} alt={item.name} />
              ) : (
                <div className="gallery-image gallery-placeholder">Kein Bild</div>
              )}
              <div className="gallery-body">
                <h3 className="gallery-title">{item.name}</h3>
                <span className="gallery-badge">{CATEGORY_LABELS[item.category]}</span>
                {item.color && (
                  <span className="gallery-meta">Farbe: {item.color}</span>
                )}
                {item.brand && (
                  <span className="gallery-meta">Marke: {item.brand}</span>
                )}
                <div className="gallery-actions">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => openEdit(item)}
                  >
                    Bearbeiten
                  </button>
                  <button
                    type="button"
                    className="btn btn-danger"
                    onClick={() => setDeleteTarget(item)}
                  >
                    Löschen
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      {formOpen && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-panel">
            <div className="modal-header">
              <h2 className="modal-title">
                {editing ? "Kleidungsstück bearbeiten" : "Neues Kleidungsstück"}
              </h2>
              <button
                type="button"
                className="modal-close"
                onClick={closeForm}
                aria-label="Schließen"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit} noValidate>
              {formError && <div className="alert alert-error">{formError}</div>}

              <div className="form-field">
                <label className="form-label" htmlFor="item-name">
                  Name
                </label>
                <input
                  id="item-name"
                  className="input"
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                  placeholder="z. B. Schwarzes Abendkleid"
                  required
                />
              </div>

              <div className="form-field">
                <label className="form-label" htmlFor="item-category">
                  Kategorie
                </label>
                <select
                  id="item-category"
                  className="input"
                  value={form.category}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, category: e.target.value as Category }))
                  }
                >
                  {CATEGORIES.map((category) => (
                    <option key={category} value={category}>
                      {CATEGORY_LABELS[category]}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-field">
                <label className="form-label" htmlFor="item-color">
                  Farbe (optional)
                </label>
                <input
                  id="item-color"
                  className="input"
                  type="text"
                  value={form.color}
                  onChange={(e) => setForm((prev) => ({ ...prev, color: e.target.value }))}
                  placeholder="z. B. Schwarz"
                />
              </div>

              <div className="form-field">
                <label className="form-label" htmlFor="item-brand">
                  Marke (optional)
                </label>
                <input
                  id="item-brand"
                  className="input"
                  type="text"
                  value={form.brand}
                  onChange={(e) => setForm((prev) => ({ ...prev, brand: e.target.value }))}
                  placeholder="z. B. Chanel"
                />
              </div>

              <div className="form-field">
                <span className="form-label">Bild (JPG, PNG oder WebP)</span>
                <label className="dropzone">
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
                    onChange={(e) => selectImage(e.target.files?.[0] ?? null)}
                  />
                  {previewUrl ? (
                    <img className="preview-image" src={previewUrl} alt="Vorschau" />
                  ) : editing?.image_url ? (
                    <AuthedImage src={editing.image_url} alt="Aktuelles Bild" className="preview-image" />
                  ) : (
                    <span className="dropzone-hint">Bild auswählen oder hier ablegen</span>
                  )}
                </label>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeForm}
                  disabled={saving}
                >
                  Abbrechen
                </button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? "Speichere …" : "Speichern"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteTarget && (
        <div className="modal-overlay" role="dialog" aria-modal="true">
          <div className="modal-panel">
            <h2 className="modal-title">Kleidungsstück löschen?</h2>
            <p className="text-muted">
              Soll „{deleteTarget.name}" wirklich gelöscht werden? Dies kann nicht
              rückgängig gemacht werden.
            </p>
            <div className="modal-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setDeleteTarget(null)}
                disabled={deleting}
              >
                Abbrechen
              </button>
              <button
                type="button"
                className="btn btn-danger"
                onClick={confirmDelete}
                disabled={deleting}
              >
                {deleting ? "Lösche …" : "Löschen"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
