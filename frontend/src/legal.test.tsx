import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import PrivacyPage from "./pages/PrivacyPage";
import ImprintPage from "./pages/ImprintPage";

describe("PrivacyPage", () => {
  it("renders the privacy policy with its sections", () => {
    render(
      <MemoryRouter>
        <PrivacyPage />
      </MemoryRouter>,
    );
    expect(
      screen.getByRole("heading", { name: "Datenschutzerklärung" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Verantwortlicher/ }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Ihre Rechte/ }),
    ).toBeInTheDocument();
  });

  it("links to the imprint page", () => {
    render(
      <MemoryRouter>
        <PrivacyPage />
      </MemoryRouter>,
    );
    expect(screen.getByRole("link", { name: "Impressum" })).toHaveAttribute(
      "href",
      "/imprint",
    );
  });
});

describe("ImprintPage", () => {
  it("renders the imprint with operator placeholders", () => {
    render(
      <MemoryRouter>
        <ImprintPage />
      </MemoryRouter>,
    );
    expect(
      screen.getByRole("heading", { name: "Impressum" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/Name des Betreibers/)).toBeInTheDocument();
    expect(screen.getByText(/Haftungshinweis/)).toBeInTheDocument();
  });
});
