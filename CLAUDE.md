@AGENTS.md

## Nur für Claude

- Der Paradox-Monitor liegt im Schwesterordner `..\Paradox-Monitor` (README dort). Er liest die Spielstände von CK3 und Stellaris; Tests dort mit `py -3 -m unittest`. Sein Lesecode gehört der Sitzung, die den Monitor betreut.
- Aufnahmen hochladen: `WEBSITE_AKTUALISIEREN.bat` im Paradox-Monitor, oder hier `py -3 scripts/publish-monitor.py [--save erster-lauf] [--no-push] [--yes]`. Das Skript fragt vor dem Push; hochladen nur mit Freigabe des Spielers. Probelauf an einer anderen Welt: `--welt ck3:… --ausgabe ORDNER` schreibt außerhalb des Repos.
- Vor jedem Hochladen von Hand: `py -3 scripts/privat-pruefen.py`. Es vergleicht das Repo mit den privaten Werten aus dem Monitor (Kontonummer, Dateinamen, Spielername), ohne sie auszugeben.
- Die Ablage des Monitors enthält Privates (`datei.pfad`, `letzte_datei`, `kampagne.spielername`). Nichts davon in Texte, Commit-Nachrichten oder die Werkstatt übernehmen.
- Vorschau: `python -m http.server` im Repo; im eingebauten Browser hell, dunkel und in Handybreite prüfen.
- Am Ende der Sitzung neben `werkstatt/LOG.md` auch `..\LETZTER_STAND.md` und `..\DECISIONS.md` im Arbeitsordner des Spielers nachziehen.
