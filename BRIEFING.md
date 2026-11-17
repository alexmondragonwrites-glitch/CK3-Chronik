# CK3-Chronik – Briefing

Stand 17.11.2026, 18:30. Entwurf nach den Antworten des Spielers vom selben Abend. Gebaut wird erst nach seiner Freigabe.

Nachtrag vom 17.11.2026: Die Freigabe zum Bau kam am selben Abend. Das Gerüst (Schritte 1 bis 4 unter „Erster Bau nach Freigabe“) steht; was gebaut ist, nennen `werkstatt/LOG.md` und `docs/ARCHITECTURE.md`.

## Ziel

Eine öffentliche Chronik der eigenen Partien in Crusader Kings III auf GitHub Pages, aufgebaut wie die AnnoChronik und die Transport Fever Chronicles. Der Spieler: „hier ist dann auch die passende chronik wo dann die daten ähnlich der anno chronik bzw tf3 chronik hinkommen sollen“.

- Repo: https://github.com/alexmondragonwrites-glitch/CK3-Chronik (öffentlich, am 17.11.2026 angelegt, noch leer). Seite später: https://alexmondragonwrites-glitch.github.io/CK3-Chronik/
- Datenquelle: der Paradox-Monitor im Schwesterordner `Paradox-Monitor`. Er liest die Spielstände und führt je Partie Aufnahmen und eine Chronik.
- Vorlage für Aufbau, Skripte und Regeln: der Schwesterordner `AnnoChronik`.
- Erste Partie: eine neue Partie in CK3 1.21 „Florin“ mit dem DLC Silk & Silver, begonnen am 17.11.2026.

## Entschieden (Spieler, 17.11.2026)

| Frage | Antwort |
|---|---|
| Wer erzählt | „Die Spielfigur“: das Tagebuch der Figur, die der Spieler gerade führt |
| Erste Partie | eine neue Partie in 1.21; Figur, Haus und Startjahr kommen aus dem Spielstand |
| Kapitel | nach Einschnitten; stirbt die Spielfigur, beginnt mit dem Erben ein neues Buch mit eigener Stimme |
| Aussehen | mittelalterliche Handschrift: Pergament, rote Rubriken, Schmuckinitialen; Farbe und Ornament je Lauf nach Haus und Kultur |
| Figur | Dossier des Spielers für die erste Figur; die Erben bekommen ihre Stimme aus dem Spielstand, bis der Spieler etwas ergänzt |

## Was aus der AnnoChronik übernommen wird

- Statische Seite ohne Framework und Backend, Schriften lokal, keine Anfragen an fremde Server, hell und dunkel, Handy und PC.
- Portal `index.html` und je Partie ein Ordner `saves/<lauf>/` mit eigener Adresse; Weltregister `data/worlds.json`, Zuordnung zur Welt im Monitor in `data/monitor-sources.json`.
- Je Partie `chronik.html` (Titelblatt, Steckbrief, Register, Kapitel, offene Fragen, Quellen, Korrekturen) und `data/` mit `meta.json`, `manifest.json`, dem Register `events.json` (nur anhängen) und `monitor/`.
- `lore/` als verbindlicher Kanon des Spielers.
- Werkstatt für Claude und Codex: `werkstatt/README.md`, `AUFGABEN.md`, `LOG.md`, je Lauf `STAND.md` und `fakten/`. Dazu `AGENTS.md`, `CLAUDE.md` und die Regeln je Lauf in `docs/`.
- GitHub Actions „Datenqualität“ prüft bei jedem Push Daten und Skripte; ausgeliefert wird über „Deploy from a branch“ (`main`, Ordner `/`).
- Regeln:
  - Belegt, Abgeleitet und Tagebuch trennen. Zahlen nur aus Aufnahmen des Monitors oder aus Angaben des Spielers.
  - Veröffentlichten Wortlaut nur zur Korrektur eines Fehlers ändern, mit Eintrag unter „Korrekturen“.
  - Neuladen wird nicht erzählt. Keine Sitzung plant die Zukunft der Partie: Der Spieler spielt, die Chronik folgt.
  - Schreibweise nach `docs/SCHREIBSTIL.md` der AnnoChronik (ruhige Sätze, positiv formuliert, ohne Schlusspointen und KI-Phrasen); die Datei wird übernommen.
- Hochladen nur mit Freigabe des Spielers („Ja, hochladen“).

## Was bei CK3 anders ist

- **Zeit:** CK3 hat ein Kalenderdatum. Register und Kapitel tragen das Spieldatum (etwa 13.2.875), daneben steht der Tag der Aufnahme.
- **Weltkennung:** die `playthrough_id` des Spielstands (`ck3:<uuid>`). Sie steht erst nach dem ersten Spielstand der Partie fest.
- **Quellen:** nur Spielstände, gelesen vom Paradox-Monitor. Ironman und Autosave überschreiben dieselbe Datei; der Monitor läuft deshalb beim Spielen mit. Ein eigenes Datum haben Geburt, Tod, Kriegsbeginn und die Erinnerungen der Figuren; alles andere trägt den Zeitraum zwischen zwei Aufnahmen.
- **Was der Spielstand verschweigt:** Ereignistexte, Entscheidungen und Gründe. Das Tagebuch erfindet dafür keine Ursachen. Was der Spieler dazu sagt (in einer Nachricht oder im Notizbuch des Monitors), geht als Quelle „Angabe des Spielers“ ein.
- **Spielerwissen:** Verdecktes bleibt draußen wie im Monitor: echte Väter, Geheimnisse, Intrigen, Schwangerschaften, geheime Glauben anderer.
- **Lesestand:** Für CK3 1.21 gibt es am 17.11.2026 noch keine passende Version des Werkzeugs rakaly, das die binären Spielstände lesbar macht. Zahlen aus 1.21 gelten als belegt, sobald der Spieler fünf Werte im Spiel verglichen hat (`geprueft.json` im Monitor).
- **Datenschutz:** Die Ablage des Monitors enthält den Pfad des Spielstands samt Kontonummer, den Dateinamen und den Spielernamen aus dem Spielstand. Das Hochlade-Skript lässt das weg; das Prüfskript schlägt an, wenn doch etwas davon im Repo landet.
- **Spielgrafik:** Porträts, Wappen, Karte und Artwork aus dem Spiel kommen nicht auf die Seite. Eigene Zeichnungen aus den Daten sind erlaubt.

## Tagebuch, Bücher und Kapitel

- Es schreibt die Spielfigur in der Ich-Form. Jede Spielfigur hat ein eigenes **Buch**. Mit dem Herrscherwechsel schließt es, und der Erbe beginnt seines mit eigener Stimme. Den Wechsel hält das Register fest; ein Tod steht dort mit Datum, die Ursache nur so, wie der Spielstand sie nennt.
- **Kapitel** schließen mit einem Einschnitt, zum Beispiel:
  - ein Krieg ist beendet;
  - ein Titel ist erlangt oder verloren;
  - eine Heirat oder die Geburt des Erben;
  - ein neuer Lehnsherr;
  - bei Kaufleuten ein Schritt der Familie nach oben.
- Claude schlägt den Einschnitt aus dem Faktenblatt vor, der Spieler bestätigt ihn. Will er ein Kapitel früher schließen, gilt sein Wort. Kapitel zählen über den ganzen Lauf fortlaufend in römischen Ziffern.
- Jedes Kapitel hat einen Stichtag: das Spieldatum der letzten verwendeten Aufnahme und den Tag dieser Aufnahme.
- Aufbau eines Kapitels wie in der AnnoChronik: Tagebucheinträge und ein knapper Bericht (Belegt) mit Spieldatum und Quelle, Abgeleitetes als Randnotiz. Die Formen wechseln, etwa Brief, Liste, Abschrift einer Urkunde, Gebet oder Rechnung.
- Was die Figur über Familie, Titel, Kriege, Bündnisse, Gold und Ansehen schreibt, folgt den Aufnahmen. Gedanken, Begegnungen und Wetter sind Erzählung. Die Menschen des Spielstands tragen ihre Namen aus dem Spiel; erfundene Menschen stehen nur im Tagebuch, nie im Register.
- **Erste Figur:** Dossier des Spielers in `lore/<figur>.md`, verbindlicher Kanon.
- **Erben:** ein Profil aus dem Spielstand (Eigenschaften, Erziehung, Fertigkeiten, Familie, Glaube, Erinnerungen) in `werkstatt/<lauf>/figuren/`. Was der Spieler ergänzt, wandert nach `lore/` und gilt dann als Kanon.
- Faktenblatt je Kapitel: `werkstatt/<lauf>/fakten/kapitel-N.md` aus den Aufnahmen des Zeitraums.

## Erscheinungsbild „Handschrift“

- Leitbild: die Hauschronik als Handschrift.
- Pergament als Papier, Tinte in Braunschwarz, Rubriken (Überschriften und Datumszeilen) in Rot, Schmuckinitialen am Kapitelanfang, schlichte Randleisten als SVG aus einem eigenen Skript.
- Schriften lokal und unter SIL OFL: eine Auszeichnungsschrift für Titel und Initialen (Unziale oder Textura; Auswahl und Lizenz werden beim Bau geprüft), EB Garamond im Text wie in den anderen Chroniken.
- Je Lauf eine Farbe und ein Ornament nach Haus und Kultur (`data-farbe` und `data-stil` wie in der AnnoChronik). Den Vorschlag für die Farbe liefert das Wappen des Hauses im Spielstand, der Spieler bestätigt.
- Textarten: Tagebuch auf getöntem Pergament mit Initiale, Bericht hell mit Quellenvermerk, Abgeleitetes als Randnotiz.
- Kontrast nach WCAG AA, geprüft am Handy und am PC, hell und dunkel.

## Aufbau des Repos (Vorschlag)

```text
CK3-Chronik/
├── index.html                  # Portal: alle Partien
├── assets/                     # handschrift.css, Schriften, Ornamente, chronik.js, portal.js
├── data/worlds.json            # Weltregister
├── data/monitor-sources.json   # Lauf → Weltkennung im Paradox-Monitor
├── lore/                       # Kanon des Spielers (Dossiers)
├── saves/<lauf>/
│   ├── index.html              # leitet auf die Chronik
│   ├── chronik.html            # Titelblatt, Steckbrief, Register, Bücher und Kapitel, Haus und Titel, offene Fragen, Quellen, Korrekturen
│   └── data/                   # meta.json, manifest.json, events.json, monitor/
├── werkstatt/                  # README, AUFGABEN, LOG, <lauf>/STAND.md, <lauf>/fakten/, <lauf>/figuren/
├── docs/                       # ARCHITECTURE.md, MONITOR.md, SCHREIBSTIL.md, <LAUF>.md
├── scripts/                    # publish-monitor.py, monitor_daten.py, fakten.py, validate-data.mjs, new-save.mjs, ornamente.py
├── .github/workflows/validate.yml
├── AGENTS.md, CLAUDE.md, README.md
└── BRIEFING.md                 # diese Datei
```

## Datenweg

1. Der Paradox-Monitor schreibt je Partie `daten/ck3/<welt>/daten.jsonl` (eine Aufnahme je Zeile), `chronik.jsonl` und `welt.json`.
2. `scripts/publish-monitor.py --save <lauf>` nimmt nur die Welt dieses Laufs (Weltkennung in `data/monitor-sources.json`). Es lässt Pfade, Dateinamen, Kontonummer und Spielernamen weg und schreibt `saves/<lauf>/data/monitor/`: den Verlauf der Kennzahlen, die gültige Chronik des Monitors und je Aufnahme den Stand der Figuren und Titel. Aufnahmen, die nach einem Neuladen verworfen sind, bleiben draußen.
3. Danach laufen die Prüfskripte. Das Skript zeigt die Änderungen und pusht erst nach Bestätigung.
4. Im Paradox-Monitor kommt `WEBSITE_AKTUALISIEREN.bat` dazu, wie im Anno-Monitor.

## Erster Bau nach Freigabe

1. Gerüst: Portal, Seite des ersten Laufs mit Titelblatt und leerem Kapitelteil, das Erscheinungsbild mit Schriften und Ornamenten.
2. Prüfskripte und die Action „Datenqualität“, Werkstatt, Doku, `AGENTS.md`, `CLAUDE.md`, `README.md`.
3. Hochlade-Skript mit Datenschutzfilter und Tests, `WEBSITE_AKTUALISIEREN.bat` im Paradox-Monitor.
4. Lokal prüfen (Browser, Handy, dunkel), dann die Freigabe für den ersten Push. Danach schaltet der Spieler Pages ein: Einstellungen → Pages → „Deploy from a branch“, `main`, `/`.
5. Kapitel I entsteht nach dem ersten Einschnitt, mit dem Dossier der ersten Figur und sobald 1.21 im Spiel bestätigt ist.

## Später möglich (nicht im ersten Bau)

- Stammbaum des Hauses, gezeichnet aus den Aufnahmen.
- Karte des Reichs je Kapitel als eigene Zeichnung im Stil der Handschrift, wie die Landkarten der AnnoChronik. Die Kartendaten des Spiels bleiben lokal.
- Handel, Handelsposten und Bezirke aus 1.21, sobald der Monitor sie liest.

## Offen

- Vom Spieler: der Vergleich von fünf Werten im Spiel. Das Dossier der ersten Figur liegt seit dem 17.11.2026 vor (`lore/joshua-von-silberfurt.md`).
- Name des Laufs. Vorschlag: „Haus <Name> · Erster Lauf“; der Hausname kommt aus dem Spielstand.
- Farbe und Ornament des ersten Laufs, sobald Haus und Kultur feststehen.
- Ob Vasallen, Rivalen und Lehnsherr im Tagebuch auftreten dürfen. Vorschlag: ja, mit ihren Namen aus dem Spiel; was sie tun, nur nach Aufnahme.
