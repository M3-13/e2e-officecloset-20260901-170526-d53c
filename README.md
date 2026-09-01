# Glamouröser Kleiderschrank-Manager

Ein Full-Stack-Web-App-MVP im Hollywood-Stil: Benutzer registrieren sich, verwalten
ihre Garderobe (Kleidungsstücke mit Bild-Upload und Kategorien), durchstöbern und
filtern sie und kombinieren Einzelteile im Outfit-Creator zu gespeicherten Outfits —
alles in einer eleganten Red-Carpet-Optik.

## Tech Stack

- **Backend**: Python 3 + FastAPI, SQLAlchemy, SQLite
- **Auth**: JWT (Bearer-Token)
- **Frontend**: React + Vite (TypeScript)
- **Styling**: CSS/Theme im Red-Carpet-Stil
- **Bilder**: Lokaler Datei-Upload mit statischem Serving

## Installation

### Backend

```bash
cd backend
python -m pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Entwicklung starten

### Backend (Port 8000)

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Beim Start legt die App das Datenbank-Schema automatisch an (`create_all`), sodass
der Server ohne manuelle Migration sofort läuft.

### Frontend (Port 5173)

```bash
cd frontend
npm run dev
```

Das Frontend ruft das Backend über relative `/api/*`-Pfade auf (Vite-Proxy → Port 8000).

## Umgebungsvariablen

| Variable          | Default                       | Beschreibung                        |
| ----------------- | ----------------------------- | ----------------------------------- |
| `DATABASE_URL`    | `sqlite:///./wardrobe.db`     | SQLAlchemy-Datenbank-URL            |
| `SECRET_KEY`      | (keine — wird generiert)      | JWT-Signierschlüssel                |
| `UPLOAD_DIR`      | `./uploads`                   | Verzeichnis für hochgeladene Bilder |
| `FRONTEND_ORIGIN` | `http://localhost:5173`       | Erlaubte CORS-Origin des Frontends  |
| `MAX_UPLOAD_MB`   | `5`                           | Maximale Bild-Upload-Größe in MB    |

### SECRET_KEY lokal erzeugen

Der JWT-Signierschlüssel wird nicht im Repo abgelegt und muss lokal gesetzt
werden. Erzeuge ihn und exportiere ihn vor dem Start (oder trage ihn in eine
`.env` ein — Vorlage siehe `backend/.env.example`):

```bash
# Linux/macOS
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Windows (PowerShell)
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

## API-Endpunkte

Alle Fehler antworten als `{"detail": "<meldung>"}`. Bis auf `/api/health`,
`/api/auth/register` und `/api/auth/login` verlangen alle Endpunkte ein
Bearer-Token (`Authorization: Bearer <token>`).

| Methode | Pfad                          | Body                                  | Antwort                        |
| ------- | ----------------------------- | ------------------------------------- | ------------------------------ |
| GET     | `/api/health`                 | —                                     | `200 {"status":"ok"}`          |
| POST    | `/api/auth/register`          | `{email, password}`                   | `200 {access_token, token_type}` |
| POST    | `/api/auth/login`             | `{email, password}`                   | `200 {access_token, token_type}` |
| GET     | `/api/auth/me`                | —                                     | `200 {id, email}`              |
| GET     | `/api/wardrobe/items`         | `?category=` (optional)               | `200 [Item]`                   |
| POST    | `/api/wardrobe/items`         | multipart `name, category, …`         | `201 Item`                     |
| GET     | `/api/wardrobe/items/{id}`    | —                                     | `200 Item`                     |
| PATCH   | `/api/wardrobe/items/{id}`    | multipart                             | `200 Item`                     |
| DELETE  | `/api/wardrobe/items/{id}`    | —                                     | `204`                          |
| GET     | `/api/images/{filename}`      | —                                     | `200 Bildbytes`                |
| GET     | `/api/outfits`                | —                                     | `200 [Outfit]`                 |
| POST    | `/api/outfits`                | `{name, item_ids}`                    | `201 Outfit`                   |
| GET     | `/api/outfits/{id}`           | —                                     | `200 Outfit`                   |
| PATCH   | `/api/outfits/{id}`           | `{name?, item_ids?}`                  | `200 Outfit`                   |
| DELETE  | `/api/outfits/{id}`           | —                                     | `204`                          |
| DELETE  | `/api/account/me`             | —                                     | `204`                          |

### Datenmodelle

- **Item**: `{id, name, category, color, brand, image_url, created_at}`
- **Outfit**: `{id, name, items: [Item]}`

## Features

- Registrierung und Anmeldung mit JWT
- Garderobe mit Bild-Upload, Kategorien und Filter
- Outfit-Creator (Kombinieren, Speichern, Öffnen, Bearbeiten, Löschen)
- Konto-Löschung mit serverseitiger Datenbereinigung
- Datenschutzerklärung und Impressum
