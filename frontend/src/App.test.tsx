import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { AuthProvider } from "./auth/AuthContext";
import App from "./App";

function renderApp() {
  return render(
    <AuthProvider>
      <App />
    </AuthProvider>,
  );
}

describe("App shell", () => {
  it("renders the navigation shell with brand and links", () => {
    renderApp();
    expect(screen.getByRole("link", { name: "Office Closet" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Garderobe" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Outfits" })).toBeInTheDocument();
  });

  it("renders the footer with privacy and imprint links", () => {
    renderApp();
    expect(screen.getByRole("link", { name: "Datenschutz" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Impressum" })).toBeInTheDocument();
  });
});
