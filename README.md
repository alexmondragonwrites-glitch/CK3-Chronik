# CK3-Chronik

**Chroniken eigener Partien in Crusader Kings III**, erzählt aus den Aufnahmen der Spielstände. Aufgebaut wie die [AnnoChronik](https://github.com/alexmondragonwrites-glitch/AnnoChronik) und die [Transport Fever Chronicles](https://github.com/alexmondragonwrites-glitch/Transport-Fever-Chronicles): statische Seite auf GitHub Pages, Register, Aufnahmen aus einem eigenen Monitor, Werkstatt für Claude und Codex.

## Läufe

- **Erster Lauf** (seit 17.11.2026, Arbeitstitel): Joshua von Silberfurt, ein Kaufmann aus dem ostfränkischen Reich, gründet 867 die Silberfurt-Gesellschaft; eine Hauschronik, erzählt in seinem Tagebuch, mit Crusader Kings III 1.21 „Florin“ und der Erweiterung Silk & Silver. Figurenkanon: [lore/joshua-von-silberfurt.md](lore/joshua-von-silberfurt.md). [Chronik](saves/erster-lauf/chronik.html) · [Regeln](docs/ERSTER-LAUF.md)

## Arbeitsweise

Das Spiel ist die Quelle, die Chronik erzählt. Der Paradox-Monitor liest die Spielstände und hält je Aufnahme fest, was im Spiel zu sehen ist. Belegtes, Abgeleitetes und das Tagebuch sind getrennt gekennzeichnet. Register und Kapitel tragen das Spieldatum, daneben steht der Tag der Aufnahme.

Es schreibt die Spielfigur. Jede Spielfigur hat ein eigenes Buch; nach ihrem Tod beginnt der Erbe ein neues. Kapitel schließen mit einem Einschnitt der Partie und zählen über den ganzen Lauf.

- [Architektur](docs/ARCHITECTURE.md) · [Aufnahmen](docs/MONITOR.md) · [Schreibregel](docs/SCHREIBSTIL.md) · [Werkstatt](werkstatt/README.md) · [Musterblatt des Erscheinungsbilds](musterblatt.html)

## Lokal ausführen

```bash
python -m http.server 8000
node scripts/validate-data.mjs
node scripts/test-pruefung.mjs
python scripts/test-monitor-daten.py
python scripts/ornamente.py --pruefen
node scripts/kontrast.mjs
```

## Datenschutz

Aus dem Monitor kommen nur gültige Aufnahmen auf die Seite. Pfade, die Steam-Kontonummer, Dateinamen der Spielstände und der Spielername bleiben beim Spieler; drei Prüfungen wachen darüber ([docs/MONITOR.md](docs/MONITOR.md)).

## Rechte

Eine private Fan-Chronik, unabhängig von Paradox Interactive. Crusader Kings ist eine Marke von Paradox Interactive AB. Bilder aus dem Spiel zeigt die Seite keine; Ornamente und Pergament sind eigene Zeichnungen aus `scripts/ornamente.py`.

Schriften: Texturina und EB Garamond unter der SIL Open Font License 1.1. Lizenztexte, Herkunft und Prüfsummen: [assets/fonts/QUELLEN.md](assets/fonts/QUELLEN.md).
