# Design — Project Identity

> This document is project-long-lived. Tokens are not changed without
> the Architect's approval. Developers MUST use these tokens
> instead of improvising their own colors/spacings.

## Style Direction

Dunkles, glamouröses Red-Carpet-Theme mit tiefem Schwarzviolett, warmem Elfenbein und Gold-Akzenten; edel wie ein Preisverleihungs-Abend, aber klar und konsistent wie ein modernes Produkt-Interface.

## Colors

- `--color-bg`: **#0E0B10**
- `--color-surface`: **#17121A**
- `--color-surface_alt`: **#1F1822**
- `--color-fg`: **#F4EDE1**
- `--color-muted`: **#A99C8E**
- `--color-border`: **#332B30**
- `--color-accent`: **#C9A24B**
- `--color-accent_hover`: **#DAB86A**
- `--color-accent_active`: **#B08A38**
- `--color-danger`: **#E5484D**
- `--color-success`: **#3BA55D**

## Typography

- `font_family`: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
- `heading_font_family`: Didot, 'Bodoni MT', 'Didot LT STD', Georgia, 'Times New Roman', serif
- `heading_weight`: 600
- `body_weight`: 400
- `size_scale`: xs: 12px; sm: 14px; md: 16px; lg: 20px; xl: 28px; 2xl: 36px

## Spacing Scale

- `--space-0`: 4px
- `--space-1`: 8px
- `--space-2`: 12px
- `--space-3`: 16px
- `--space-4`: 24px
- `--space-5`: 32px
- `--space-6`: 48px

## Border-Radii

- `--radius-sm`: 4px
- `--radius-md`: 8px
- `--radius-lg`: 16px
- `--radius-pill`: 999px

## Components

### Button

Primary: padding 12px 24px, radius pill, bg=accent #C9A24B, fg=#1A1410, font-weight 600, letter-spacing 0.02em, min-height 44px (mobile tap), transition 150ms; hover bg=accent_hover #DAB86A; active bg=accent_active #B08A38; disabled opacity 0.5, kein Pointer. Secondary: transparent, border 1px solid border #332B30, fg=fg #F4EDE1; hover border=accent, bg=rgba(201,162,75,0.08); active bg=rgba(201,162,75,0.14). Danger: bg=transparent, border 1px solid danger, fg=danger; hover bg=rgba(229,72,77,0.12).

### Card

bg=surface #17121A, border 1px solid border #332B30, radius lg 16px, padding 16px, box-shadow 0 8px 24px rgba(0,0,0,0.35); hover border=accent bei 40% Deckkraft, translateY(-1px).

### Input

bg=surface_alt #1F1822, border 1px solid border #332B30, radius md 8px, padding 12px 14px, min-height 48px, color fg; placeholder color muted; focus border=accent #C9A24B, box-shadow 0 0 0 3px rgba(201,162,75,0.22); Fehlerzustand border=danger #E5484D.

### Modal

Overlay bg=rgba(14,11,16,0.72), backdrop-filter blur(4px); Panel bg=surface #17121A, border 1px solid border, radius lg 16px, max-width 480px, padding 24px; Schließen-Button 44x44px, radius md, hover bg=surface_alt.

### Nav/Header

Sticky top 0, height 64px, bg=rgba(14,11,16,0.85), backdrop-filter blur(8px), border-bottom 1px solid border; Logo in heading_font_family, Farbe accent, Größe lg; Inhalt zentriert in Container, Abstand links/rechts 16px mobil, 24px desktop.

### FilterChip

radius pill, border 1px solid border, padding 8px 16px, min-height 44px, bg transparent, color muted; active bg=accent #C9A24B, color=#1A1410, border=accent, font-weight 600; hover border=accent.

### Alert

radius md 8px, padding 12px 16px, display flex, gap 8px, Icon 20px; Fehler: bg=rgba(229,72,77,0.12), border 1px solid danger #E5484D, color fg; Erfolg: bg=rgba(59,165,93,0.12), border 1px solid success #3BA55D.

### ImageUpload/Dropzone

border 2px dashed border #332B30, radius lg 16px, padding 24px, min-height 160px, bg=surface_alt #1F1822, zentrierter Inhalt; hover border=accent, bg=rgba(201,162,75,0.05); Vorschau: Bild object-fit cover, radius md, max-height 320px.

### GalleryItem

bg=surface #17121A, radius lg 16px, overflow hidden, border 1px solid border; Bild ratio 3:4, object-fit cover, width 100%; Textblock padding 12px, Titel fw 600, Kategorie als Badge in muted.

### EmptyState

padding 48px 16px, Text zentriert, Überschrift heading_font_family Farbe muted, Beschreibung color muted, Button-Abstand 16px.

### OutfitPreview

Grid 2 Spalten (mobil 1 Spalte unter 640px), gap 16px; Slot bg=surface_alt #1F1822, border 1px solid border, radius lg, padding 16px, min-height 220px; aktiver Slot border=accent #C9A24B, box-shadow 0 0 0 3px rgba(201,162,75,0.18); leere Slot-Beschriftung muted.

## Layout Principles

- Container max-width 1200px, horizontal zentriert, Seitenabstand 16px mobil / 24px ab 640px.
- Breakpoints: <640px mobil (einspaltig), 640–1024px Tablet (2 Spalten für Galerie), >1024px Desktop (Galerie-Grid auto-fill minmax(180px, 1fr)).
- Galerie-Grid: display grid, gap 16px, auto-fill minmax(180px, 1fr); Outfit-Creator zweispaltig ab 640px.
- Abstände zwischen Sektionen 32px, zwischen Karten 16px; Formularfelder vertikal mit 16px Abstand.
- Sticky Header 64px; Footer mit Impressum/Datenschutz auf jeder Seite erreichbar, bg=surface, border-top 1px solid border.
- Alle interaktiven Elemente (Buttons, Chips, Links) mindestens 44px Touch-Ziel, Fokus-Zustand sichtbar mit Gold-Ring.
- Red-Carpet-Akzente sparsam: Gold nur für primäre Aktionen, aktive Zustände und Highlights; große Flächen dunkel halten.
