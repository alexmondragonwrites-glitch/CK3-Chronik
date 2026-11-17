# CK3-Chronik – Hinweise für KI-Sitzungen

Statische Website (GitHub Pages) mit Chroniken eigener Partien in Crusader Kings III, aufgebaut wie die AnnoChronik und die Transport Fever Chronicles. Jede Partie ist ein **Lauf**. Erster Lauf: `saves/erster-lauf/`, begonnen am 17.11.2026 mit CK3 1.21, erste Spielfigur Joshua von Silberfurt; „Erster Lauf“ ist ein Arbeitstitel. Es erzählt die Spielfigur in ihrem Tagebuch; je Spielfigur ein Buch, die Kapitel zählen über den ganzen Lauf. Claude Code und Codex arbeiten daran, auch parallel.

## Zuerst lesen

1. `werkstatt/README.md`: Ablauf, Regeln, wer was kann.
2. `werkstatt/AUFGABEN.md`: wer gerade woran arbeitet. Vor dem Ändern eintragen.
3. Die obersten Einträge in `werkstatt/LOG.md`.
4. Für den ersten Lauf: `werkstatt/erster-lauf/STAND.md`, `docs/ERSTER-LAUF.md` und der verbindliche Figurenkanon `lore/joshua-von-silberfurt.md`.
5. Vor einem Kapitel: `docs/SCHREIBSTIL.md`. Zu den Daten: `docs/MONITOR.md`. Zum Aufbau: `docs/ARCHITECTURE.md`. Die Entscheidungen des Spielers: `BRIEFING.md`.

## Kurzregeln

- Vor dem Arbeiten und vor jedem Push `git fetch origin`; zusammenführen statt überschreiben. Kein `--force`.
- Hochladen nur mit Freigabe des Spielers („Ja, hochladen“).
- Keine Zahlen erfinden. Belegt, Abgeleitet und Tagebuch trennen. Zahlen nur aus Aufnahmen des Paradox-Monitors oder aus Angaben des Spielers.
- Crusader Kings zählt nach dem Kalender: Register und Kapitel tragen das Spieldatum, daneben steht der Tag der Aufnahme. Ohne eigenes Datum im Spielstand steht der Zeitraum zwischen zwei Aufnahmen.
- Der Spielstand nennt keine Ursachen, Ereignistexte oder Entscheidungen. Niemand erfindet sie; was der Spieler dazu sagt, ist „Angabe des Spielers“.
- Verdecktes bleibt draußen: echte Väter, Geheimnisse, Intrigen, Schwangerschaften, geheime Glauben anderer.
- Veröffentlichten Wortlaut nur zur Korrektur eines Fehlers ändern, mit Eintrag unter „Korrekturen“. `data/events.json` ist append-only.
- Figuren: `lore/` ist verbindlicher Kanon des Spielers. Die Seite gibt ein Dossier nur im Wortlaut wieder (`data-kanon`, von der Datenprüfung verglichen). Offenes bleibt offen; die Geschichte entsteht aus dem tatsächlichen Spielverlauf. Menschen des Spielstands tragen ihre Namen aus dem Spiel, erfundene stehen nur im Tagebuch.
- Neuladen (Rücksprung des Spieldatums) wird nicht erzählt. Keine Sitzung plant die Zukunft der Partie.
- Läufe nicht vermischen.
- Öffentliches Repo: keine Zugangsdaten, keine lokalen Pfade, keine Steam-Kontonummer, keine Dateinamen von Spielständen, kein Spielername aus dem Spielstand, keine Rohdaten des Monitors, keine Spielgrafik (Porträts, Wappen, Karte, Artwork).
- Schriften und Ornamente entstehen nur aus `scripts/schriften.py` und `scripts/ornamente.py`. Nichts von fremden Servern laden.

## Prüfen

```bash
node scripts/validate-data.mjs
node scripts/test-pruefung.mjs
python3 scripts/test-monitor-daten.py
python3 scripts/ornamente.py --pruefen
node scripts/kontrast.mjs
```

Wer den Paradox-Monitor neben dem Repo hat, dazu `python3 scripts/privat-pruefen.py`. Dieselben Prüfungen laufen in `.github/workflows/validate.yml`.
