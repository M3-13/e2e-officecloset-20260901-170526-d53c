export default function ImprintPage() {
  return (
    <section className="container page">
      <h1 className="page-title">Impressum</h1>

      <h2>Angaben gemäß § 5 DDG</h2>
      <p>
        <strong>Betreiber:</strong> [Name des Betreibers]
        <br />
        <strong>Anschrift:</strong> [Straße und Hausnummer]
        <br />
        [Postleitzahl und Ort]
        <br />
        [Land]
      </p>

      <h2>Kontakt</h2>
      <p>
        <strong>E-Mail:</strong> [kontakt@beispiel.de]
        <br />
        <strong>Telefon:</strong> [Telefonnummer]
      </p>

      <h2>Vertretungsberechtigt</h2>
      <p>[Name der vertretungsberechtigten Person]</p>

      <h2>Haftungshinweis</h2>
      <p>
        Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir keine Haftung
        für die Inhalte externer Links. Für den Inhalt der verlinkten Seiten
        sind ausschließlich deren Betreiber verantwortlich.
      </p>
    </section>
  );
}
