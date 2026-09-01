import { useState, type CSSProperties, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { register as apiRegister, me as fetchMe } from "../api/auth";
import { apiErrorMessage } from "../api/client";

const TOKEN_KEY = "token";

const formStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-3)",
};

const fieldStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "var(--space-1)",
};

const labelStyle: CSSProperties = {
  fontSize: "var(--size-sm)",
  color: "var(--color-muted)",
};

const cardStyle: CSSProperties = {
  maxWidth: 440,
  margin: "0 auto",
};

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const auth = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const response = await apiRegister(email, password);
      localStorage.setItem(TOKEN_KEY, response.access_token);
      try {
        const user = await fetchMe();
        auth.login(response.access_token, user);
        navigate("/wardrobe");
      } catch (meErr) {
        localStorage.removeItem(TOKEN_KEY);
        setError(apiErrorMessage(meErr));
      }
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="container page">
      <div className="card" style={cardStyle}>
        <h1 className="page-title">Registrieren</h1>
        <form onSubmit={handleSubmit} noValidate style={formStyle}>
          <label htmlFor="register-email" style={fieldStyle}>
            <span style={labelStyle}>E-Mail</span>
            <input
              id="register-email"
              name="email"
              type="email"
              className="input"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
            />
          </label>
          <label htmlFor="register-password" style={fieldStyle}>
            <span style={labelStyle}>Passwort</span>
            <input
              id="register-password"
              name="password"
              type="password"
              className="input"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="new-password"
              required
            />
          </label>
          {error ? (
            <div className="alert alert-error" role="alert">
              {error}
            </div>
          ) : null}
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Registrieren …" : "Registrieren"}
          </button>
        </form>
        <p className="text-muted" style={{ marginTop: "var(--space-3)" }}>
          Schon ein Konto? <Link to="/login">Jetzt anmelden</Link>
        </p>
      </div>
    </section>
  );
}
