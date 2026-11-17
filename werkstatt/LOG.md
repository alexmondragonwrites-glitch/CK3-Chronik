# Werkstatt-Log

## 2026-11-17 – Neue Felder des Monitors für das Hochlade-Skript (Claude)

- Meldung der Hauptsitzung: Der Monitor liest die Welt des ersten Laufs beim nächsten Start aus seiner Sicherung neu. Neu im Schnappschuss sind die Gesetze der Spielfigur (`spieler.gesetze`), je Titel `landlos` und im Block `datei` die Version des Lesers (`leser`); neu in der Chronik die Arten `gesetz` und `sitz`.
- `scripts/monitor_daten.py`: `gesetze`, `landlos` und `leser` stehen in den Erlaubnislisten, die Tests decken sie ab. Chronikzeilen jeder Art gingen schon bisher durch. Am Abend lagen die neuen Felder im Monitor noch nicht vor; geprüft ist an erfundenen Daten, an der echten Welt erst nach dem Neuaufbau.
- `docs/MONITOR.md`: Abschnitt „Neuaufbau im Monitor“. Die Nummern der Aufnahmen bleiben, die `id` einer Chronikzeile nicht unbedingt; Register und Kapitel verweisen nie auf sie.
- Hochgeladen auf Freigabe („Ja, hochladen“) mit dem Commit, der diesen Eintrag enthält.

## 2026-11-17 – Erster Push (Claude)

- Der Spieler hat Vorschau und Stand gesehen und freigegeben („Ja, hochladen“). Hochgeladen: `afde4c9`, 59 Dateien, das Gerüst mit dem Dossier der ersten Spielfigur.
- Vor dem Commit liefen alle Prüfungen: Datenprüfung, 25 untergeschobene Fälle, 17 Python-Tests, Kontrast, Ornamente, `privat-pruefen.py`.
- GitHub Pages schaltet der Spieler ein: Einstellungen → Pages → „Deploy from a branch“, `main`, `/`. Die Seite liegt dann unter `https://alexmondragonwrites-glitch.github.io/CK3-Chronik/`.

## 2026-11-17 – Dossier eingebunden, Weltkennung eingetragen (Claude)

- Auftrag der Hauptsitzung am Abend: das Dossier `lore/joshua-von-silberfurt.md` einbinden, ohne es umzuschreiben; die Welt `ck3:a2be71f2-d985-4ba1-b9d7-05841d0295fc` für den ersten Lauf eintragen; beim Arbeitstitel bleiben; die Entscheidung des Spielers zum Ort festhalten.
- **Seite:** neuer Abschnitt I „Die erste Spielfigur“ mit dem Dossier im Wortlaut (Kasten mit `data-kanon`), die übrigen Abschnitte zählen von II bis VIII. Steckbrief und „Haus und Titel“ nennen aus der ersten Aufnahme (Spieldatum 1.1.867) Name, Haus und Dynastie, Titel und Regierung, mit dem Vermerk „im Spiel noch nicht verglichen“. Zahlen stehen keine auf der Seite. Unter „Offene Fragen“ steht, was das Dossier offen lässt. Neue Quellen: Q2 Dossier, Q3 Paradox-Monitor, Q4 Angabe des Spielers zum Ort („wir gehen mit der reise nach frankfurt“).
- **Wortlaut gesichert:** `validate-data.mjs` vergleicht jeden Absatz des Dossiers (bis vor „Offen“) mit der Seite; `test-pruefung.mjs` prüft das mit drei neuen Fällen (jetzt 25).
- **Daten:** `world_id` in `data/monitor-sources.json` und `meta.json`, `spielfigur` in `meta.json`, Beschreibung in `data/worlds.json` und im Portal. Aufnahmen sind noch keine geschrieben: Die Hauptsitzung liest die Welt noch einmal neu ein, die Lesung ist im Spiel nicht verglichen.
- **Hochlade-Skript:** Aus dem Block `datei` kommt neu die Zahl der Platzhalter-Abschnitte von rakaly in `lesung` (nur gezählt).
- **Ort:** Wortlaut des Spielers und die Lesart der Hauptsitzung stehen in `erster-lauf/STAND.md` und `docs/ERSTER-LAUF.md`. Kein Kapitel daraus; das ist Stoff für Kapitel I. Nachtrag am selben Abend: Der Spieler hat die Lesart bestätigt („passt“); beide Dateien und die Quelle Q4 führen den Ort seitdem als entschieden.
- Geprüft: Datenprüfung, 25 Fälle, 17 Python-Tests, Kontrast, Ornamente, `privat-pruefen.py`; Vorschau der Laufseite hell, dunkel und als Handy.

## 2026-11-17 – Gerüst der CK3-Chronik gebaut (Claude)

- Auftrag: Schritte 1 bis 4 aus `BRIEFING.md`, „Erster Bau nach Freigabe“. Der Spieler hat den Bau am Abend des 17.11.2026 freigegeben. Alles liegt lokal, ohne Commit; der erste Push wartet auf „Ja, hochladen“.
- **Seiten:** Portal `index.html`, `saves/erster-lauf/` (Titelblatt, Steckbrief, Register, Bücher und Kapitel, Haus und Titel, offene Fragen, Quellen, Korrekturen; noch ohne Buch und Kapitel), `musterblatt.html` mit allen Bausteinen und Blindtext. „Erster Lauf“ ist Arbeitstitel; Q1 ist das Briefing.
- **Erscheinungsbild „Handschrift“** (`assets/handschrift.css`): Pergament als berechnete Kachel, braunschwarze Tinte, rote Rubriken, Schmuckinitialen auf Rautengrund (abwechselnd rot und blau), Blattranke als Randleiste, Titelrahmen mit Eckrosetten, Vierpass. Hell und dunkel nach der Einstellung des Geräts. Farbe des Hauses über `data-farbe` (blau, rot, grün, purpur, schwarz, gold), Ornament über `data-stil` (bisher `ranke`). Alle Ornamente aus `scripts/ornamente.py`.
- **Schriften:** Texturina für Titel, Rubriken und Initialen, EB Garamond für den Text; beide SIL OFL 1.1 ohne „Reserved Font Name“, geladen aus `github.com/google/fonts` (Stand `7af0d90`), auf lateinische Schrift verkleinert, als WOFF2. Ergänzt: Kapitälchen für das deutsche f und die Umlaute in EB Garamond. Herkunft, Prüfsummen und Änderungen in `assets/fonts/QUELLEN.md`, Bau mit `scripts/schriften.py`.
- **Hochladen:** `scripts/publish-monitor.py` liest eine Welt aus `daten/ck3/<welt>/` des Paradox-Monitors und schreibt `saves/<lauf>/data/monitor/` (`index.json`, `verlauf.json`, `chronik.json`, `aufnahmen/aufnahme-NNNN.json`). Verworfene Aufnahmen bleiben draußen und verschwinden wieder, wenn sie schon veröffentlicht waren. Drei Sicherungen gegen Privates: Erlaubnislisten, Muster, genaue Werte aus dem Monitor (`docs/MONITOR.md`). Im Paradox-Monitor liegt `WEBSITE_AKTUALISIEREN.bat`.
- **Prüfungen:** `validate-data.mjs` (Register, Bücher und Kapitel, Aufnahmen, Schriften mit Prüfsumme, fremde Server, Datenschutz), `test-pruefung.mjs` (22 untergeschobene Fälle, jeder gemeldet), `test-monitor-daten.py` (17 Tests, darunter ein Durchlauf mit erfundenem Monitor bis zum Push auf ein Repo auf Zeit), `kontrast.mjs` (300 Paarungen, am knappsten 4,81 : 1), `ornamente.py --pruefen`, `privat-pruefen.py`. Die GitHub-Prüfung „Datenqualität“ führt sie bei jedem Push aus, dazu das Anlegen eines Laufs.
- **Geprüft am 17.11.2026:** alle Prüfungen grün. Vorschau über einen lokalen Server in Chrome: Portal, Laufseite und Musterblatt in hell und dunkel, 1280 und 1440 Pixel breit und als Handy (390 Pixel); keine Überbreite, keine Anfrage an fremde Server, keine Fehler in der Konsole. Probeläufe des Hochlade-Skripts mit zwei Welten des Monitors, Ausgabe außerhalb des Repos, ohne Fund von Privatem. In Firefox und Safari ist die Seite nicht angesehen.
- **Während des Baus dazugekommen**, beides von anderen Sitzungen: das Dossier `lore/joshua-von-silberfurt.md` und im Monitor die erste Welt aus 1.21 mit neuen Feldern für Kaufleute (Ritus, Sitz, Tributpflichtige, Art der Bindung an den Gönner); die Felder stehen in den Erlaubnislisten. Die Seite nennt Figur und Haus noch nicht: Name des Laufs, Weltkennung und Dossier auf der Seite stehen unter „Offen“ in `AUFGABEN.md`.
- **Entscheidungen:** Texturina als Auszeichnungsschrift (Textura, gut lesbar, OFL ohne Namensvorbehalt). Quellenverweise von der Seite auf Markdown zeigen auf GitHub; `.nojekyll`, damit Pages die Dateien unverändert ausliefert. Die Weltkennung trägt das Skript ein, wenn genau eine Welt zu `suche` passt, sonst wartet es auf `--welt`.
