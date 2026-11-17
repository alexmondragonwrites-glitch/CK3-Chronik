# Aufgaben

Wer etwas anfängt, trägt sich unter „In Arbeit“ ein (wer, seit wann, welche Dateien). Fertiges wandert nach „Zur Prüfung“ oder „Erledigt“.

## In Arbeit

Noch nichts.

## Zur Prüfung

- **Kapitel I „Die Reise nach Frankfurt“** (Claude, 17.11.2026): Erstes Buch, Spieldatum 1.1.867 bis 2.4.867, vom Spieler in der Vorschau bestätigt („Passt so“) und freigegeben („Ja, hochladen“), online seit dem 17.11.2026. Prüfen: Zahlen und Spieldaten in Bericht, Randnotiz und Register gegen `erster-lauf/fakten/kapitel-1.md`; das Tagebuch gegen `docs/SCHREIBSTIL.md` und gegen das, was `erster-lauf/STAND.md` als erzählt und als offen führt.
- **Gerüst der CK3-Chronik mit der ersten Spielfigur** (Claude, 17.11.2026): Portal, Seite des ersten Laufs mit Titelblatt, Dossier von Joshua von Silberfurt im Wortlaut, Steckbrief und leerem Kapitelteil, Erscheinungsbild „Handschrift“ mit Schriften und Ornamenten, Musterblatt, Prüfskripte und GitHub-Prüfung, Hochlade-Skript mit Datenschutzfilter und Tests, Werkstatt und Doku. Die Weltkennung ist eingetragen. Online seit `afde4c9`. Prüfen: Wortlaut des Dossiers gegen `lore/`, Erlaubnislisten in `scripts/monitor_daten.py` gegen die Ablage des Monitors, Erscheinungsbild in Firefox und Safari (bisher nur in Chrome angesehen).

## Offen

- **Name des Laufs:** „Erster Lauf“ ist Arbeitstitel. Vorschlag an den Spieler: „Haus von Silberfurt · Erster Lauf“. Nach seiner Bestätigung Titelblatt, Portal, `data/worlds.json`, `meta.json`, README und AGENTS nachziehen.
- **Farbe und Ornament des Laufs** nach Haus und Kultur; der Spieler wählt am Musterblatt (`musterblatt.html`).
- **Erste Aufnahmen hochladen:** `WEBSITE_AKTUALISIEREN.bat` im Paradox-Monitor oder `py -3 scripts/publish-monitor.py --save erster-lauf`; mit Freigabe des Spielers, der dazu noch nichts gesagt hat. Version 1.21.0 ist seit dem 17.11.2026 im Spiel bestätigt. Am besten nach dem nächsten Neuaufbau der Welt im Monitor (Leser 3), dann tragen alle Aufnahmen denselben Lesestand und den Tag des Umzugs.
- **Nach dem Neuaufbau im Monitor:** `py -3 scripts/fakten.py --save erster-lauf --kapitel 1 --bis 0867-04-02` erneut laufen lassen (Datum von Umzug und Gönner aus dem Vertrag).
- **Liutberts Titel:** Wie nennt ihn das Spiel? In den Daten heißt er nur „Mainz“. Frage an den Spieler; bis dahin steht „Erzbistum“ nirgends.
- **Kapitel II:** Stoff ab dem 2.4.867 (`erster-lauf/STAND.md`); den Einschnitt bestätigt der Spieler.
- **Später möglich** (Briefing): Stammbaum des Hauses aus den Aufnahmen; Karte des Reichs je Kapitel als eigene Zeichnung; Handel, Handelsposten und Bezirke aus 1.21, sobald der Monitor sie liest.

## Erledigt

- **GitHub Pages** (Spieler, 17.11.2026): eingeschaltet, „Deploy from a branch“, `main`, `/`. Die Seite liegt unter `https://alexmondragonwrites-glitch.github.io/CK3-Chronik/`; nach `bab7a25` ausgeliefert und im Browser geprüft (Portal und Laufseite, keine Fehler, keine Anfragen an andere Server).
- **Neue Felder des Monitors im Hochlade-Skript** (Claude, 17.11.2026): Gesetze, landlose Titel, Version des Lesers; `docs/MONITOR.md` mit dem Abschnitt zum Neuaufbau. Online seit `bab7a25`.
- **Faktenblatt-Skript** (Claude, 17.11.2026): `scripts/fakten.py` erzeugt je Kapitel ein Blatt aus den gefilterten Aufnahmen des Zeitraums, hängt das von Hand geführte Beiblatt an, prüft alles auf Privates und bleibt bei gleichen Aufnahmen und gleichem Beiblatt byte-gleich; im Kopf steht der jüngste Lesestand der Spielversion. Fünf Tests. Dazu in den Erlaubnislisten die Felder des Monitors zum Vertrag mit Lehnsherr oder Gönner (`lehnsherr_seit`, `lehnsherr_vertrag`). Online seit dem Upload von Kapitel I am 17.11.2026.
