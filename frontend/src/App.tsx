import { BrowserRouter, Routes, Route, Navigate, Link, NavLink } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import WardrobePage from "./pages/WardrobePage";
import OutfitsPage from "./pages/OutfitsPage";
import AccountPage from "./pages/AccountPage";
import PrivacyPage from "./pages/PrivacyPage";
import ImprintPage from "./pages/ImprintPage";

function NavShell() {
  const { isAuthenticated, logout } = useAuth();
  return (
    <header className="app-header">
      <div className="container header-inner">
        <Link to="/" className="logo">
          Office Closet
        </Link>
        <nav className="nav" aria-label="Hauptnavigation">
          <NavLink
            to="/wardrobe"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Garderobe
          </NavLink>
          <NavLink
            to="/outfits"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Outfits
          </NavLink>
          <NavLink
            to="/account"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Konto
          </NavLink>
          {isAuthenticated ? (
            <button type="button" className="nav-link nav-logout" onClick={logout}>
              Abmelden
            </button>
          ) : (
            <NavLink
              to="/login"
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              Anmelden
            </NavLink>
          )}
        </nav>
      </div>
    </header>
  );
}

function Footer() {
  return (
    <footer className="app-footer">
      <div className="container footer-inner">
        <span className="footer-brand">Office Closet</span>
        <nav className="footer-links" aria-label="Rechtliches">
          <Link to="/privacy">Datenschutz</Link>
          <Link to="/imprint">Impressum</Link>
        </nav>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="app-shell">
        <NavShell />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Navigate to="/wardrobe" replace />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/wardrobe" element={<WardrobePage />} />
            <Route path="/outfits" element={<OutfitsPage />} />
            <Route path="/account" element={<AccountPage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="/imprint" element={<ImprintPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
