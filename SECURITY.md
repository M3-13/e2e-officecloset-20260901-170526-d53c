VERDICT: BLOCKED

## Scanner-Hinweis

Die vorgesehenen Scanner waren nicht aktiv:

- `bandit` – `[skipped] bandit not installed`
- `semgrep` – `[skipped] semgrep not installed`
- `pip-audit` / `npm audit` – nicht ausgeführt

Daraus können keine Aussagen zu bekannten CVEs in Python-/npm-Abhängigkeiten abgeleitet werden. Die folgende Bewertung basiert ausschließlich auf dem sichtbaren Code und der sichtbaren Konfiguration.

## Zusammenfassung

Das Produkt erfüllt viele Anforderungen sauber: Benutzer-Isolation über `WHERE user_id = current_user.id`, Owner-only-Bildabruf, grundsätzliches Rate-Limiting, explizite CORS-Origin sowie Account-Löschung mit Dateibereinigung. Blockierend ist jedoch der **leere Standardwert für den JWT-Signaturschlüssel**, wodurch sich gültige Tokens für beliebige Benutzer fälschen lassen. Zusätzlich ist das Upload-Limit unvollständig.

---

## Befund 1 — Kritisch: JWT-Signaturschlüssel mit leerem Standardwert

**Betroffene Stellen:**

- `backend/app/config.py` – `return os.environ.get("SECRET_KEY", "")`
- `backend/app/auth.py` – `jwt.encode(... settings.secret_key ... HS256)` / `jwt.decode(... settings.secret_key ... HS256)`
- `backend/app/main.py` – kein Startcheck auf einen gesetzten Schlüssel

**Problem:**

Beim Start ohne gesetzte Umgebungsvariable `SECRET_KEY` ist der Signaturschlüssel ein leerer String. Ein Angreifer kann dann selbst einen gültigen HS256-Token erzeugen, z. B.:

```python
jwt.encode({"sub": "1", "exp": ...}, "", algorithm="HS256")
```

Damit ist die gesamte Authentifizierung ausgehebelt. Der Angreifer kann beliebige `user_id`s annehmen, auf fremde Garderoben/Outfits/Bilder zugreifen und Konten Dritter lesen, ändern oder löschen.

**Konkrete Behebung:**

- `SECRET_KEY` darf keinen unsicheren Default mehr haben.
- In `config.py` prüfen, dass der Wert vorhanden und ausreichend lang ist, z. B.:

```python
@property
def secret_key(self) -> str:
    value = os.environ.get("SECRET_KEY")
    if not value or len(value) < 32:
        raise RuntimeError("SECRET_KEY muss gesetzt und mindestens 32 Zeichen lang sein")
    return value
```

- Zusätzlich in der FastAPI-Startup-Phase (`lifespan`) validieren, damit ein Start ohne Schlüssel sofort scheitert und nicht stillschweigend unsicher läuft.
- `.env.example` darf nur einen Platzhalter enthalten, keinen echten Produktionsschlüssel.

---

## Befund 2 — Hoch: Upload-Größenlimit wird nicht durchgängig vor dem Puffern durchgesetzt

**Betroffene Stellen:**

- `backend/app/wardrobe.py` – `_check_content_length()`
- `backend/app/wardrobe.py` – `create_item()` / `update_item()` mit `await request.form()`
- `backend/app/wardrobe.py` – `_read_image()`

**Problem:**

AC-13 verlangt, dass die Maximalgröße **vor** dem Einlesen des Request-Bodys durchgesetzt wird. `_check_content_length()` prüft ausschließlich den `Content-Length`-Header. Bei:

- fehlendem Header,
- `Transfer-Encoding: chunked`,
- einem absichtlich zu kleinen oder gefälschten `Content-Length`-Wert

wird der gesamte Multipart-Body durch `await request.form()` gepuffert. Ein authentifizierter Angreifer kann dadurch sehr große Uploads senden und den Server über Speicher-/CPU-Last destabilisieren. In Kombination mit Befund 1 ist das sogar ohne eigene Registrierung möglich.

**Konkrete Behebung:**

- Body-Limit auf ASGI-/Middleware-Ebene durchsetzen, nicht nur über `Content-Length`.
- Alternativ den Upload-Stream selbst auswerten und sofort mit `413` abbrechen, sobald die Grenze überschritten wird.
- Falls die verwendete Starlette-Version es unterstützt: `await request.form(max_part_size=..., max_files=..., max_fields=...)` verwenden oder die Datei partiell aus dem Stream lesen.
- Die Prüfung darf nicht auf den Header allein vertrauen.

---

## Befund 3 — Mittel: Bildvalidierung nur über Dateiendung, kein Inhaltstyp-/Magic-Byte-Check

**Betroffene Stellen:**

- `backend/app/wardrobe.py` – `_read_image()`
- `backend/app/images.py` – `get_image()`, `MEDIA_TYPES`

**Problem:**

Es wird ausschließlich `os.path.splitext(filename)[1]` validiert. Eine Datei mit beliebigem Inhalt kann z. B. als `evil.png` hochgeladen und unter `image/png` ausgeliefert werden. Ein echter Bild-Check fehlt. Außerdem fehlt der Header `X-Content-Type-Options: nosniff`, sodass der Browser potenziell Inhalte raten kann.

**Konkrete Behebung:**

- Vor dem Speichern den Dateiinhalt mit einer Bild-Bibliothek wie Pillow öffnen und prüfen, z. B.:

```python
from PIL import Image

try:
    img = Image.open(io.BytesIO(content))
    img.verify()
except Exception:
    raise HTTPException(status_code=400, detail="Ungültige Bilddatei")
```

- Beim Ausliefern von Bildern in `get_image()` zusätzlich `X-Content-Type-Options: nosniff` setzen.
- Optional: Bilder serverseitig neu enkodieren, um eingebettete Fremdinhalte zu entfernen.

---

## Befund 4 — Niedrig: Rate-Limiter und Client-IP hinter Proxys verbesserungswürdig

**Betroffene Stellen:**

- `backend/app/auth.py` – `_client_ip()`
- `backend/app/auth.py` – `RateLimiter`

**Problem:**

`_client_ip()` nutzt `request.client.host`. Hinter einem Reverse-Proxy sehen alle Clients wie dieselbe IP aus; das Login-/Registrierungs-Limit kann dann alle Nutzer gemeinsam treffen oder leicht umgangen werden. Zusätzlich wachsen die Einträge in `self._hits` unbegrenzt, da alte IP-Schlüssel nie entfernt werden.

**Konkrete Behebung:**

- Nur bei vertrauenswürdigem Proxy `X-Forwarded-For` bzw. `X-Real-IP` auswerten, nicht pauschal.
- Einen periodischen Cleanup für abgelaufene Einträge einführen.
- IPv6-Normalisierung beachten.

---

## Befund 5 — Niedrig: CORS erlaubt unnötig breite Methoden und Header

**Betroffene Stelle:**

- `backend/app/main.py` – `CORSMiddleware`

**Problem:**

`allow_credentials=True` ist korrekt mit einer konkreten Origin kombiniert. `allow_methods=["*"]` und `allow_headers=["*"]` sind jedoch breiter als nötig. Das erfüllt AC-15 zwar nicht direkt als Verstoß gegen die Origin-Regel, ist aber unnötige Angriffsfläche.

**Konkrete Behebung:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Befund 6 — Niedrig: JWT im `localStorage`

**Betroffene Stellen:**

- `frontend/src/api/client.ts` – `getToken()`
- `frontend/src/auth/AuthContext.tsx`
- `frontend/src/pages/LoginPage.tsx` / `RegisterPage.tsx`

**Problem:**

Der Bearer-Token liegt im `localStorage`. Sollte später einmal eine XSS-Lücke entstehen, kann der Token ausgelesen werden. Im aktuellen sichtbaren Frontend-Code wurde keine XSS-Lücke festgestellt, daher ist dies als Härtungshinweis einzuordnen.

**Konkrete Behebung:**

- Sofern möglich, auf ein HttpOnly-SameSite-Cookie umstellen.
- Ergänzend eine Content-Security-Policy setzen, die Inline-Skripte und externe Quellen einschränkt.
- Derzeit keine produktiven Funktionen brechen, da die Anwendung keine Drittanbieter-Skripte oder Inline-JavaScript benötigt.

---

## Ergebnis

Der kritische JWT-Schlüssel-Default hebelt die Authentifizierung vollständig aus und rechtfertigt ein BLOCKED. Nach Behebung von Befund 1 sowie des Upload-Limits (Befund 2) ist eine erneute Prüfung sinnvoll.