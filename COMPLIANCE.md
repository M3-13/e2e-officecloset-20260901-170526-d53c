VERDICT: BLOCKED

# Compliance-Bericht — Glamouröser Kleiderschrank-Manager (Hollywood-Stil)

Geprüft wurde der gegenwärtig sichtbare Stand des gemergten Produkts. Maßgeblich sind nur die tatsächlich vorhandenen Quelldateien, nicht Spekulationen über nicht sichtbare Dateiabschnitte. Der Projekttyp ist eine öffentlich erreichbare Full-Stack-Webanwendung mit Benutzerkonten, Upload personenbezogener Bilder und einer React-Oberfläche.

---

## 1. GDPR / Datenschutz (DSGVO)

### G1 — Leeres JWT-Secret als Produktionsstandard (critical)
**Datei:** `backend/app/config.py`  
Die Eigenschaft `secret_key` hat den Default `""`. In `backend/app/auth.py` wird genau dieser Wert in `_create_token` und `get_current_user` für `jwt.encode` / `jwt.decode` verwendet. Wenn `SECRET_KEY` nicht gesetzt ist, werden Tokens mit einem leeren Secret signiert. Jeder Angreifer kann damit gültige Tokens für beliebige Benutzer-IDs erzeugen und sich als fremder Benutzer ausgeben. Dadurch sind alle personenbezogenen Daten (E-Mail, Garderobe, Outfits, hochgeladene Bilder) ungeschützt abrufbar. Dies verletzt Art. 32 DSGVO und macht die Authentifizierung im Sinne von AC-16 wirkungslos.

**Remedy:**
- In `backend/app/config.py` darf `secret_key` nicht leer sein. Mindestens folgende Änderung:
  ```python
  @property
  def secret_key(self) -> str:
      value = os.environ.get("SECRET_KEY")
      if not value:
          raise RuntimeError("SECRET_KEY muss gesetzt sein (min. 32 Zeichen).")
      return value
  ```
- Zusätzlich in `backend/app/auth.py` vor dem Signieren prüfen: `if len(settings.secret_key) < 32: raise RuntimeError(...)`.
- In `backend/.env.example` einen starken Beispielwert dokumentieren, in `README.md` die verpflichtende Setzung beschreiben.

---

### G2 — Authentifizierungs-Token und Nutzerdaten im localStorage ohne XSS-Gegenmaßnahmen (high)
**Dateien:** `frontend/src/auth/AuthContext.tsx`, `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/RegisterPage.tsx`  
Der JWT (`TOKEN_KEY`) und das Benutzerobjekt (`USER_KEY`) werden im `localStorage` gespeichert. localStorage ist für JavaScript im selben Browserkontext zugänglich. Ohne Content Security Policy (CSP) können erfolgreiche XSS-Angriffe den Token auslesen. Die Backend-Antworten setzen keine Security-Header (kein CSP, kein `X-Content-Type-Options`, kein `Referrer-Policy`).

**Remedy:**
- In `backend/app/main.py` eine Middleware für Security-Header ergänzen, insbesondere:
  ```
  Content-Security-Policy: default-src 'self'; img-src 'self' blob:; style-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer
  ```
- Falls der Token zwingend im localStorage bleiben muss, ist die CSP zwingend. Vorzugsweise den JWT in ein httpOnly-Cookie auslagern (dann zusätzlich CSRF-Schutz erforderlich).
- In der Datenschutzerklärung die Speicherung des Tokens im Browser offenlegen (siehe G5).

---

### G3 — Account-Löschung entfernt Dateien nicht zuverlässig (high)
**Dateien:** `backend/app/account.py`, `backend/app/storage.py`  
`delete_account` löscht zuerst den Benutzer (`db.delete(user); db.commit()`) und ruft danach `delete_user_files(user_id)` auf. `delete_user_files` verwendet `shutil.rmtree(user_dir, ignore_errors=True)`. Schlägt die Dateilöschung fehl (z. B. Berechtigungsproblem, offene Datei), wird der Fehler still geschluckt, und die hochgeladenen Bilder bleiben dauerhaft auf der Festplatte. Der Benutzer erhält keine Information über die unvollständige Löschung. Das verletzt das Recht auf Löschung gemäß Art. 17 DSGVO und AC-19.

**Remedy:**
- In `backend/app/storage.py` `delete_user_files` nicht mit `ignore_errors=True` aufrufen, sondern:
  ```python
  def delete_user_files(user_id: int) -> None:
      user_dir = os.path.join(settings.upload_dir, str(user_id))
      try:
          shutil.rmtree(user_dir)
      except FileNotFoundError:
          pass
      except OSError as exc:
          logger.exception("Löschen der Nutzerdateien fehlgeschlagen: %s", exc)
          raise
  ```
- In `backend/app/account.py` die Reihenfolge ändern: zunächst Dateien löschen, danach die DB-Transaktion committen. Wenn die Dateilöschung scheitert, mit 500 antworten und den Fehler protokollieren, nicht den Benutzer „erfolgreich“ löschen.
- Zusätzlich prüfen, ob das Verzeichnis tatsächlich nicht mehr existiert; bei Bedarf einen Wiederholungsmechanismus implementieren.

---

### G4 — Keine Passwort-Mindestanforderung (medium)
**Dateien:** `backend/app/schemas.py`, `backend/app/auth.py`  
Das Pydantic-Modell `Register` definiert `password: str` ohne `min_length` oder Komplexitätsanforderung. Ein Passwort mit einem Zeichen ist möglich. Das erhöht das Risiko erfolgreicher Brute-Force- oder Credential-Stuffing-Angriffe erheblich und verletzt Art. 32 DSGVO.

**Remedy:**
- In `backend/app/schemas.py` z. B. `password: str = Field(min_length=8)` verwenden.
- Optional eine Passwortstärke-Prüfung (z. B. zxcvbn) ergänzen.
- Die Validierung im Frontend kann ergänzend als Hinweis erfolgen, ist aber nicht ausreichend.

---

### G5 — Datenschutzerklärung unvollständig (medium)
**Datei:** `frontend/src/pages/PrivacyPage.tsx`  
Die Datenschutzerklärung enthält keine vollständigen Pflichtangaben nach Art. 13 DSGVO. Es fehlen insbesondere:
- Beschwerderecht bei einer Aufsichtsbehörde,
- Hinweis, ob die Bereitstellung der Daten gesetzlich oder vertraglich vorgeschrieben ist,
- Angabe, dass ein Authentifizierungs-Token im Browser (localStorage) gespeichert wird,
- ggf. Hinweis auf automatisierte Entscheidungsfindung (hier nicht vorhanden, aber die Negativangabe fehlt).

**Remedy:**
- In `frontend/src/pages/PrivacyPage.tsx` die Abschnitte ergänzen:
  ```tsx
  <h2>9. Beschwerderecht bei einer Aufsichtsbehörde</h2>
  <p>Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren.</p>
  <h2>10. Bereitstellungspflicht</h2>
  <p>Die Bereitstellung Ihrer E-Mail-Adresse und eines Passworts ist erforderlich, um ein Konto zu erstellen und die Anwendung zu nutzen.</p>
  <h2>11. Speicherung im Browser</h2>
  <p>Zur Authentifizierung speichert die Anwendung einen technisch notwendigen Token in Ihrem Browser (localStorage).</p>
  <h2>12. Automatisierte Entscheidungsfindung</h2>
  <p>Es findet keine automatisierte Entscheidungsfindung einschließlich Profiling statt.</p>
  ```

---

### G6 — Hochgeladene Bilder können Metadaten (z. B. EXIF/Standort) enthalten (medium)
**Dateien:** `backend/app/wardrobe.py`, `backend/app/storage.py`  
`_read_image` prüft nur die Dateiendung und die Größe, entfernt aber keine Metadaten. Hochgeladene Fotos können eingebettete GPS-Koordinaten oder andere personenbezogene Informationen enthalten, die unverschlüsselt gespeichert werden.

**Remedy:**
- Vor dem Speichern in `backend/app/storage.py` die Bilddaten durch eine Bildbibliothek (z. B. Pillow) öffnen und ohne EXIF-Daten neu speichern.
- Alternativ in der Datenschutzerklärung darauf hinweisen, dass Metadaten nicht entfernt werden; besser ist die serverseitige Entfernung.

---

## 2. EU Cyber Resilience Act (CRA)

### C1 — Keine dokumentierte Security-Umgebung, keine SBOM, kein Patch-Management (high)
**Dateien:** `backend/requirements.txt`, `frontend/package-lock.json`, `README.md`, `DESIGN.md`  
Die Anwendung ist ein Produkt mit digitalen Elementen. Eine Softwarekomponentenliste (SBOM) fehlt. Es gibt kein dokumentiertes Verfahren zur Aktualisierung und Behebung von Schwachstellen in Abhängigkeiten. Für die CRA-Konformität muss der Hersteller Sicherheitsupdates über einen definierten Zeitraum bereitstellen können.

**Remedy:**
- In der CI-Pipeline einen SBOM-Generator (z. B. CycloneDX oder Syft) einbinden und das Ergebnis im Repository ablegen.
- `pip-audit` und `npm audit` in die Pipeline aufnehmen; Schwachstellen automatisch blockieren.
- In `README.md` oder `DESIGN.md` einen Abschnitt „Sicherheitsupdates und Patch-Management“ ergänzen: Prozess, Verantwortlichkeiten, Support-Zeitraum.

---

### C2 — Keine dokumentierten Sicherheitseigenschaften des Produkts (medium)
**Dateien:** `DESIGN.md`, `README.md`  
Die tatsächlich implementierten Sicherheitsmaßnahmen (JWT-Auth, Rate-Limiting, CORS, Upload-Limit, user-spezifische Dateipfade) sind im Code vorhanden, aber nicht als dokumentierte Sicherheitseigenschaften ausgewiesen.

**Remedy:**
- In `DESIGN.md` einen Abschnitt „Security Properties“ ergänzen:
  - Authentisierung mit JWT (HS256, Ablaufzeit),
  - Autorisierung auf Benutzer-IDs,
  - Rate-Limiting für Login/Registration,
  - Upload-Begrenzung und erlaubte Dateitypen,
  - Eigentümer-basierter Bildabruf,
  - CORS-Origin-Beschränkung.

---

### C3 — Fehlende standardmäßige Sicherheitsheader (high)
**Datei:** `backend/app/main.py`  
Die Anwendung setzt weder CSP, `X-Content-Type-Options`, `Referrer-Policy` noch andere Security-Header. Dies verstärkt das unter G2 beschriebene XSS-Risiko und entspricht nicht „Security by default“.

**Remedy:**
- Middleware in `backend/app/main.py` ergänzen, die die unter G2 genannten Header setzt.
- Die CSP muss die eigenen Ressourcen erlauben, insbesondere `img-src 'self' blob:`. Nur so funktioniert der Bildabruf über `URL.createObjectURL` weiterhin korrekt (Reconcile-Prüfung: der CSP-Entwurf erlaubt `blob:` für Bilder, daher ist die Produktfunktion nicht blockiert).

---

## 3. EU AI Act

Keine KI-Funktion im Produkt erkennbar. Es gibt kein maschinelles Lernen, keine generative KI, kein Profiling. Der EU AI Act findet daher auf den sichtbaren Stand keine Anwendung.

---

## 4. Pflichttexte und UI

### T1 — Impressum enthält nur Platzhalter, ist nicht rechtsgültig (high)
**Datei:** `frontend/src/pages/ImprintPage.tsx`  
Das Impressum enthält ausschließlich Platzhalter wie `[Name des Betreibers]`, `[Straße und Hausnummer]`, `[kontakt@beispiel.de]`. Ein Impressum nach § 5 DDG erfordert tatsächliche Angaben. Eine Seite, die nur Platzhalter darstellt, erfüllt die gesetzliche Anbieterkennzeichnung nicht.

**Remedy:**
- In `frontend/src/pages/ImprintPage.tsx` die Platzhalter durch die tatsächlichen Daten des Betreibers ersetzen (Name, Anschrift, Kontakt, Vertretungsberechtigter).
- Vor Auslieferung an Endkunden darf die App nicht mit Platzhalter-Impressum betrieben werden.

---

### T2 — Datenschutzerklärung verweist auf unvollständiges Impressum (high)
**Datei:** `frontend/src/pages/PrivacyPage.tsx`  
Der Abschnitt „Verantwortlicher“ verweist auf das Impressum, das jedoch nur Platzhalter enthält. Damit ist der Verantwortliche nicht identifizierbar. Das verletzt die Informationspflicht nach Art. 13 Abs. 1 lit. a DSGVO.

**Remedy:**
- Sobald das Impressum reale Daten enthält, ist die Verknüpfung ausreichend. Bis dahin darf das Produkt nicht öffentlich bereitgestellt werden.
- Zusätzlich in der Datenschutzerklärung die konkreten Kontaktdaten des Verantwortlichen wiederholen.

---

### T3 — Consent-Banner nicht erforderlich, Zustand in Ordnung (low / Hinweis)
**Dateien:** `frontend/index.html`, `frontend/src/App.tsx`  
Es werden keine Drittanbieter-Ressourcen geladen (keine externen Schriftarten, Skripte oder Bilder). Der im Browser gespeicherte Token ist technisch notwendig für die Authentifizierung. Ein Cookie-/Consent-Banner ist daher nicht erforderlich. Ein pauschal eingefügter Consent-Banner würde die Nutzung ohne datenschutzrechtliche Notwendigkeit erschweren.

**Remedy:** Keine Änderung. Es sollte kein Banner eingebaut werden, solange keine zustimmungspflichtigen Cookies oder Dienste eingesetzt werden.

---

### T4 — Footer-Verlinkung von Datenschutz und Impressum erfüllt AC-17 (low)
**Datei:** `frontend/src/App.tsx`  
Die Links sind im Footer vorhanden und von jeder Seite erreichbar. Die Anforderung ist formal erfüllt.

**Remedy:** Keine Änderung.

---

## 5. Barrierefreiheit / Accessibility (WCAG / BITV / EAA)

### A1 — Modale Dialoge ohne erkennbare ARIA-Rolle und Fokussteuerung (medium)
**Datei:** `frontend/src/pages/WardrobePage.tsx`  
Im CSS sind `.modal-overlay` und `.modal-panel` definiert. Der sichtbare Ausschnitt zeigt keinen `role="dialog"`, kein `aria-modal`, kein `aria-labelledby` und keine Fokusverwaltung (Fokusfalle, Rückkehr zum auslösenden Element). Ein modaler Dialog ohne diese Merkmale ist für Tastatur- und Screenreader-Nutzer nicht bedienbar.

**Remedy:**
- Für jedes Modal in `WardrobePage.tsx`:
  ```tsx
  <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  ```
- Beim Öffnen den Fokus auf das erste fokussierbare Element setzen, beim Schließen zurück auf den Auslöser.
- Escape-Taste schließt das Modal.
- Fokus innerhalb des Dialogs halten.
- Der Schließen-Button muss einen zugänglichen Namen haben (z. B. `aria-label="Schließen"`), nicht nur ein `×`.

---

### A2 — Fehlermeldungen sind nicht mit den Eingabefeldern verknüpft (low)
**Dateien:** `frontend/src/pages/LoginPage.tsx`, `frontend/src/pages/RegisterPage.tsx`  
Fehlermeldungen verwenden `role="alert"`, aber die betroffenen Eingabefelder sind nicht per `aria-describedby` mit der Fehlermeldung verbunden.

**Remedy:**
- Den Fehlermeldungen eine `id` geben und an den zugehörigen Inputs `aria-describedby="<id>"` setzen.
- Beispiel:
  ```tsx
  <div className="alert alert-error" role="alert" id="login-error">
  ...
  <input id="login-email" aria-describedby={error ? "login-error" : undefined} ... />
  ```

---

### A3 — Farbkontraste nicht formal validiert (low / Hinweis)
**Datei:** `frontend/src/styles/theme.css`  
Die Kombinationen wirken kontrastreich, wurden aber nicht automatisiert geprüft. Für den öffentlichen Vertrieb sollte eine Prüfung nach WCAG 2.1 AA erfolgen.

**Remedy:**
- Farbpaare (z. B. `--color-muted` auf `--color-bg`) mit einem Kontrastprüfer testen und bei Bedarf anpassen.
- In der CI kann ein Lighthouse- oder Axe-Scan die Grundlage bilden.

---

## Ergebnis / Begründung des Verdikts

Die Anwendung ist funktional weit fortgeschritten und erfüllt zentrale Anforderungen wie benutzerbezogene Isolation, geschützte Bildabrufe, Rate-Limiting und explizite CORS-Konfiguration. Allerdings besteht mit dem leeren Standardwert für `SECRET_KEY` ein fundamentaler Sicherheitsmangel: Die Authentifizierung kann ohne jeglichen Aufwand ausgehebelt werden, wodurch alle personenbezogenen Daten aller Benutzer zugänglich werden. Dies ist eine klare Verletzung von Art. 32 DSGVO und macht das Produkt in der vorliegenden Form nicht verkehrsfähig. Daher: **BLOCKED**.

Zusätzlich bestehen behebbare Mängel: unvollständiges Impressum, unvollständige Datenschutzerklärung, unsichere Dateilöschung, fehlende Sicherheitsheader, fehlende Passwortrichtlinie und unvollständige Barrierefreiheit der Modaldialoge. Diese Mängel sind im Normalbetrieb behebbar, ändern aber nichts am fundamentalen Blocker durch den JWT-Secret-Default.