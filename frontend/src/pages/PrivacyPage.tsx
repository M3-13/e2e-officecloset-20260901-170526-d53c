import { Link } from "react-router-dom";

export default function PrivacyPage() {
  return (
    <section className="container page">
      <h1 className="page-title">Datenschutzerklärung</h1>
      <p className="text-muted">Stand: 01.09.2026</p>

      <h2>1. Verantwortlicher</h2>
      <p>
        Verantwortlich für die Verarbeitung personenbezogener Daten im Sinne der
        Datenschutz-Grundverordnung (DSGVO) ist der Betreiber dieser Anwendung.
        Die         vollständigen Betreiberangaben finden Sie im{" "}
        <Link to="/imprint">Impressum</Link>.
      </p>

      <h2>2. Allgemeines zur Datenverarbeitung</h2>
      <p>
        Wir verarbeiten personenbezogene Daten ausschließlich, soweit dies zur
        Bereitstellung der Funktionen dieser Anwendung erforderlich ist. Die
        Verarbeitung erfolgt auf Grundlage von Art. 6 Abs. 1 lit. b DSGVO
        (Vertragserfüllung) sowie Art. 6 Abs. 1 lit. f DSGVO (berechtigtes
        Interesse am sicheren und funktionsfähigen Betrieb).
      </p>

      <h2>3. Verarbeitete Daten</h2>
      <p>
        Bei der Nutzung der Anwendung können folgende personenbezogene Daten
        verarbeitet werden:
      </p>
      <ul>
        <li>
          <strong>Bestandsdaten:</strong> E-Mail-Adresse, die bei der
          Registrierung eines Kontos angegeben wird.
        </li>
        <li>
          <strong>Zugangsdaten:</strong> Das Passwort wird ausschließlich in
          verschlüsselter Form (Hash) gespeichert.
        </li>
        <li>
          <strong>Nutzungsdaten:</strong> Inhalte, die Sie selbst anlegen, etwa
          Kleidungsstücke und Outfits in Ihrer Garderobe sowie die von Ihnen
          hochgeladenen Bilder.
        </li>
      </ul>

      <h2>4. Zweck der Verarbeitung</h2>
      <p>
        Die Daten werden verarbeitet, um die Anwendung bereitzustellen, Ihr
        Konto zu verwalten, Ihre Garderobe und Ihre Outfits zu speichern und den
        Zugriff auf Ihre Daten zu ermöglichen.
      </p>

      <h2>5. Speicherdauer</h2>
      <p>
        Personenbezogene Daten werden gelöscht, sobald der Zweck der
        Verarbeitung entfällt oder Sie Ihr Konto löschen. Mit der Löschung Ihres
        Kontos werden auch die zugehörigen Inhalte, einschließlich hochgeladener
        Bilder, entfernt.
      </p>

      <h2>6. Ihre Rechte</h2>
      <p>Ihnen stehen nach der DSGVO folgende Rechte zu:</p>
      <ul>
        <li>Recht auf Auskunft (Art. 15 DSGVO)</li>
        <li>Recht auf Berichtigung (Art. 16 DSGVO)</li>
        <li>Recht auf Löschung (Art. 17 DSGVO)</li>
        <li>Recht auf Einschränkung der Verarbeitung (Art. 18 DSGVO)</li>
        <li>Recht auf Datenübertragbarkeit (Art. 20 DSGVO)</li>
        <li>Recht auf Widerspruch (Art. 21 DSGVO)</li>
      </ul>
      <p>
        Zur Ausübung dieser Rechte wenden Sie sich an die im Impressum genannten
        Kontaktdaten.
      </p>

      <h2>7. Datensicherheit</h2>
      <p>
        Wir treffen geeignete technische und organisatorische Maßnahmen, um Ihre
        Daten vor Verlust, Missbrauch und unbefugtem Zugriff zu schützen. Der
        Zugriff auf Ihre Daten ist durch eine Anmeldung mit persönlichem Konto
        geschützt.
      </p>

      <h2>8. Weitergabe an Dritte</h2>
      <p>
        Eine Weitergabe Ihrer personenbezogenen Daten an Dritte erfolgt nicht,
        sofern dies nicht gesetzlich vorgeschrieben ist.
      </p>
    </section>
  );
}
