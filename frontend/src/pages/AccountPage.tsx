import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { removeAccount } from "../api/account";
import { apiErrorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export default function AccountPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!user) {
    return (
      <section className="container page">
        <h1 className="page-title">Konto</h1>
        <div className="empty-state">
          <h2>Nicht angemeldet</h2>
          <p>Melde dich an, um dein Konto zu verwalten.</p>
          <Link to="/login" className="btn btn-primary">
            Anmelden
          </Link>
        </div>
      </section>
    );
  }

  async function handleDelete(): Promise<void> {
    setDeleting(true);
    setError(null);
    try {
      await removeAccount();
      logout();
      navigate("/register", { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err));
      setDeleting(false);
      setConfirming(false);
    }
  }

  function startConfirm(): void {
    setError(null);
    setConfirming(true);
  }

  function cancelConfirm(): void {
    setError(null);
    setConfirming(false);
  }

  return (
    <section className="container page">
      <h1 className="page-title">Konto</h1>
      <div className="card" style={{ maxWidth: 480 }}>
        <p className="text-muted" style={{ marginTop: 0 }}>
          Angemeldet als
        </p>
        <p>{user.email}</p>

        {error ? (
          <div className="alert alert-error" role="alert" style={{ marginBottom: 16 }}>
            {error}
          </div>
        ) : null}

        {confirming ? (
          <div>
            <p>
              Möchtest du dein Konto wirklich löschen? Deine Garderobe, Outfits und
              hochgeladenen Bilder werden dauerhaft entfernt.
            </p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <button
                type="button"
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? "Wird gelöscht …" : "Endgültig löschen"}
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={cancelConfirm}
                disabled={deleting}
              >
                Abbrechen
              </button>
            </div>
          </div>
        ) : (
          <button type="button" className="btn btn-danger" onClick={startConfirm}>
            Konto löschen
          </button>
        )}
      </div>
    </section>
  );
}
