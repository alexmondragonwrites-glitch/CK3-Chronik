# CK3-Chronik · Architektur

Ein Repository für beliebig viele Partien in Crusader Kings III, aufgebaut wie die AnnoChronik und die Transport Fever Chronicles. Jede Partie heißt hier **Lauf**. Sie hat ein eigenes Verzeichnis, eine eigene Adresse und eine eindeutige Weltkennung aus dem Paradox-Monitor. Ausgeliefert wird statisch über GitHub Pages, ohne Framework, Backend oder fremde Server.

## Grundsätze

1. **Daten vor Deutung:** Belegtes, Abgeleitetes und Erzähltes sind sichtbar getrennt.
2. **Archiv statt Überschreiben:** Das Register wächst nur; jede gültige Aufnahme bleibt als eigene Datei stehen.
3. **Manifest statt fester Verweise:** `data/manifest.json` jedes Laufs nennt die aktuelle Seite und die Aufnahmen.
4. **Läufe getrennt:** Figuren, Häuser und Ereignisse eines Laufs kommen in keinem anderen vor.
5. **Datenschutz:** keine Pfade, Kontonummern, Dateinamen von Spielständen, kein Spielername und keine Spielgrafik im öffentlichen Repo; geprüft bei jedem Push.
6. **Reproduzierbar:** Prüfskripte und GitHub Actions überwachen Register, Verweise, Aufnahmen, Schriften, Ornamente und Kontrast.
7. **Schlank:** reines HTML, CSS und JavaScript, Schriften lokal, hell und dunkel, Handy und PC.

## Repository

```text
/
├── index.html                  # Portal: alle Läufe (data/worlds.json)
├── musterblatt.html            # alle Bausteine des Erscheinungsbilds mit Blindtext; gehört zu keinem Lauf
├── assets/
│   ├── handschrift.css         # Erscheinungsbild „Handschrift“ (Variablen, Bausteine); je Lauf data-farbe und data-stil an <html>
│   ├── chronik.js              # Seite eines Laufs: Register, Zeile zu den Aufnahmen
│   ├── portal.js               # Portal: Karten aus dem Weltregister
│   ├── musterblatt.js          # Musterblatt: Farbe des Hauses umschalten
│   ├── ranke*.svg, rahmen-*.svg, vierpass.svg, initiale-grund.svg, pergament-*.png, zeichen.svg
│   │                           # Ornamente und Pergament, alle aus scripts/ornamente.py
│   └── fonts/                  # Texturina, EB Garamond (SIL OFL), Lizenztexte, QUELLEN.md
├── data/
│   ├── worlds.json             # Weltregister
│   └── monitor-sources.json    # Lauf → Weltkennung im Paradox-Monitor
├── lore/                       # Kanon des Spielers (Dossiers)
├── saves/<lauf>/
│   ├── index.html              # leitet auf latestReport
│   ├── chronik.html            # die Chronik
│   └── data/                   # meta.json, manifest.json, events.json, monitor/
├── werkstatt/                  # Abstimmung der KI-Sitzungen (README, AUFGABEN, LOG, <lauf>/)
├── scripts/
│   ├── publish-monitor.py      # Aufnahmen aus dem Paradox-Monitor, Upload nach Bestätigung
│   ├── monitor_daten.py        # Auswahl und Datenschutzfilter (getestet in test-monitor-daten.py)
│   ├── privat-pruefen.py       # lokal: sucht die privaten Werte aus dem Monitor im ganzen Repo
│   ├── validate-data.mjs       # Datenprüfung (getestet in test-pruefung.mjs)
│   ├── kontrast.mjs            # Kontrast der Farben nach WCAG AA
│   ├── new-save.mjs            # neuen Lauf anlegen
│   ├── ornamente.py            # Ornamente und Pergament erzeugen
│   └── schriften.py            # Schriften aus den Originalen bauen und prüfen
├── docs/                       # ARCHITECTURE.md, MONITOR.md, SCHREIBSTIL.md, <LAUF>.md
├── .github/workflows/validate.yml
├── .nojekyll, .gitattributes   # Pages liefert unverändert aus; Textdateien überall mit LF
└── AGENTS.md, CLAUDE.md, README.md, BRIEFING.md
```

## Datenmodell

- `data/worlds.json`: je Lauf `id`, `name`, optional `untertitel`, `path` (`saves/<id>/`), `page`, `status` (`laufend` oder `abgeschlossen`), `started`, bei abgeschlossenen Läufen `ended`, `description`.
- `data/monitor-sources.json`: je Lauf `save`, `name`, `world_id` (`ck3:<playthrough_id>` oder `null`) und, solange die Kennung fehlt, `suche` (`angelegt_ab`, `spielversion`, `name`, `start`). Ein abgeschlossener Lauf trägt `abgeschlossen` mit `datum` und `hinweis`.
- `saves/<id>/data/meta.json`: `id`, `name`, `name_status`, `game`, `game_version`, `status`, `started`, optional `farbe` und `stil` (wie an `<html>`), `spielfigur` (Name der ersten Spielfigur und ihr Dossier unter `lore/`), `buecher` (je Spielfigur ein Eintrag, in der Reihenfolge der Bücher), `monitor.world_id`.
- Figurenkanon auf der Seite: Ein Kasten mit `data-kanon="lore/<name>.md"` gibt das Dossier im Wortlaut wieder. Die Datenprüfung vergleicht jeden Absatz der Datei bis vor „## Offen“ mit der Seite; der Zitatblock am Anfang der Datei ist der Rahmen der Werkstatt und zählt nicht mit.
- `saves/<id>/data/events.json` (Register, nur anhängen): je Eintrag `id` (`<lauf>-NNNN`), **entweder** `spieldatum` (`JJJJ-MM-TT`, eigenes Datum aus dem Spielstand) **oder** `zeitraum` (`[von, bis]`, Spieldaten zweier Aufnahmen; `von` darf `null` sein) oder ersatzweise `game_date_label`; dazu `recorded` (Tag der Aufnahme), `kind` (`fakt` = Belegt, `rekonstruktion` = Abgeleitet), `category`, `title`, `description`, `source` (Quellennummern wie `Q1`), optional `chapter` (Nummer des Kapitels) und `correction` (`date`, `note`).
- Aufnahmen: siehe `docs/MONITOR.md`.

Spieldaten stehen überall wie im Monitor: vierstellig mit führenden Nullen (`0867-01-01`). Die Seite zeigt sie als `1.1.867`.

Verweise von einer Seite auf Markdown-Dateien des Repos (Kanon in `lore/`, Briefing) zeigen auf GitHub (`…/blob/main/…`): Dort ist Markdown lesbar dargestellt, GitHub Pages liefert es nur als Rohtext aus. Die leere Datei `.nojekyll` sorgt dafür, dass Pages alle Dateien unverändert ausliefert.

## Bücher und Kapitel

Jede Spielfigur hat ein Buch: `<section class="hs-buch" id="buch-N">` in `chronik.html`. Darin stehen die Kapitel als `<article class="hs-kapitel" id="kapitel-N">`. Bücher zählen ab 1, Kapitel zählen über alle Bücher fortlaufend; die Prüfung achtet auf beides. Die Bausteine eines Kapitels zeigt `musterblatt.html`, die Regeln stehen in `docs/<LAUF>.md`.

## Erscheinungsbild

`assets/handschrift.css` hält alle Farben als Variablen, hell und dunkel nach der Einstellung des Geräts.

- **Farbe des Laufs** (`data-farbe` an `<html>`): `blau` (Vorgabe), `rot`, `gruen`, `purpur`, `schwarz`, `gold`, nach den Tinkturen der Wappen. Sie färbt Kopf und Fuß, Verweise, jede zweite Initiale und die Blätter der Randleiste im Tagebuch. Rubriken bleiben rot.
- **Ornament des Laufs** (`data-stil`): bisher `ranke`. Ein neuer Stil braucht seine Masken in `scripts/ornamente.py`, einen Block `:root[data-stil="…"]` im Stylesheet und einen Eintrag in `STILE` in `scripts/new-save.mjs`.
- **Ornamente** entstehen nur aus `scripts/ornamente.py`. Nach einer Änderung dort: `py -3 scripts/ornamente.py`, dann `node scripts/kontrast.mjs`.
- **Schriften:** `assets/fonts/QUELLEN.md` nennt Herkunft, Lizenz, Prüfsummen und was gegenüber den Originalen geändert ist.

## Neuer Lauf

```bash
node scripts/new-save.mjs --id zweiter-lauf --name "Haus Beispiel" --untertitel "Zweiter Lauf" --version "1.21" --farbe gruen
```

Danach steht er im Portal, im Weltregister und im Hochlade-Skript. Die Weltkennung trägt `publish-monitor.py` ein, sobald genau eine Welt im Monitor zu `suche` passt, sonst mit `--welt`.

## Lokal ansehen und prüfen

```bash
python -m http.server 8000
node scripts/validate-data.mjs
node scripts/test-pruefung.mjs
python scripts/test-monitor-daten.py
python scripts/ornamente.py --pruefen
node scripts/kontrast.mjs
python scripts/privat-pruefen.py        # nur dort, wo der Paradox-Monitor neben dem Repo liegt
```

Dann http://localhost:8000 öffnen. Direkte `file://`-Aufrufe laden Register und Aufnahmen wegen `fetch` nicht.
