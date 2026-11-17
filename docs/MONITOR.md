# Aufnahmen aus dem Paradox-Monitor

Der Paradox-Monitor liegt beim Spieler im Schwesterordner `Paradox-Monitor`. Er beobachtet die Spielstände von Crusader Kings III, liest jeden neuen Stand von einer Kopie und vergleicht ihn mit dem vorigen Stand derselben Partie. Je Partie führt er einen Ordner `daten/ck3/<welt>/` mit `daten.jsonl` (eine Aufnahme je Zeile), `chronik.jsonl` und `welt.json`. `scripts/publish-monitor.py` bringt davon die gültigen Aufnahmen auf die Seite.

Ironman und Autosave überschreiben dieselbe Datei. Der Monitor läuft deshalb beim Spielen mit; was er nicht gelesen hat, gibt es später nicht mehr.

## Hochladen

Im Paradox-Monitor `WEBSITE_AKTUALISIEREN.bat` doppelklicken, oder hier:

```text
py -3 scripts/publish-monitor.py                    alle laufenden Läufe aus data/monitor-sources.json, fragt vor dem Upload
py -3 scripts/publish-monitor.py --save erster-lauf  nur ein Lauf
py -3 scripts/publish-monitor.py --no-push          nur lokal schreiben und prüfen
py -3 scripts/publish-monitor.py --yes              ohne Rückfrage
py -3 scripts/publish-monitor.py --save erster-lauf --welt ck3:…                    Weltkennung des Laufs festlegen
py -3 scripts/publish-monitor.py --save erster-lauf --welt ck3:… --ausgabe ORDNER   Probelauf außerhalb des Repos
```

Ablauf: GitHub-Stand nachziehen (nur Fast-Forward), Welt des Laufs bestimmen, Dateien bauen, auf Privates prüfen, nur Geändertes schreiben, `validate-data.mjs` ausführen, das Repo nach den privaten Werten aus dem Monitor durchsuchen, Änderungen zeigen, nach Bestätigung committen und pushen. Schlägt eine Prüfung an, wird nichts committet. Ohne neue Aufnahmen entsteht kein Commit.

**Welt des Laufs:** Steht in `data/monitor-sources.json` eine `world_id`, gilt sie. Fehlt sie, sucht das Skript im Monitor nach den Angaben unter `suche` (`angelegt_ab`, `spielversion`, `name`, `start`). Passt genau eine Welt, trägt es ihre Kennung in `monitor-sources.json` und `meta.json` ein; das Manifest zeigt danach auf `data/monitor/index.json`. Passen mehrere, nennt es sie und wartet auf `--welt`. Beginnt der Spieler die Partie neu, entsteht im Monitor eine neue Welt; dann stellt eine Sitzung die Kennung mit `--welt` um, nachdem der Spieler bestätigt hat, welche Partie zur Chronik gehört.

Steht bei einem Lauf `abgeschlossen` (Datum und Hinweis), überspringt das Skript ihn, solange kein `--save` ihn nennt.

Der Probelauf mit `--ausgabe` schreibt in einen Ordner außerhalb des Repos, trägt nichts ein und lädt nichts hoch. Er dient dem Testen an einer anderen Welt des Monitors; deren Daten bleiben draußen.

## Was veröffentlicht wird

`saves/<lauf>/data/monitor/`:

- `index.json`: Weltkennung, Name der Welt im Monitor, Zahl der gültigen Aufnahmen, verworfene Aufnahmen und Neuladen (nur gezählt), Spieldatum von und bis, Zeitpunkt des Speicherns von und bis, die Spielversionen, der Lesestand der letzten Aufnahme und die Liste der Aufnahmen (`nr`, `spieldatum`, `gespeichert_um`, `spielversion`, `lesestand`, Datei).
- `verlauf.json`: je gültiger Aufnahme eine Zeile mit den Kennzahlen: Gold, Einkommen, Prestige, Frömmigkeit, Einfluss, Heeresstärke, Aufgebot, Grafschaften im Reich, Zahl der Titel und Vasallen, lebende Hausmitglieder, Ruhm der Dynastie, Stress, Gesundheit, Schrecken, Legitimität. Dabei stehen Spieldatum, Spielfigur (Kennung und Name) und die Spielzeit der Partie in Sekunden.
- `chronik.json`: die gültige Chronik des Monitors: Herrscherwechsel, Tode, Geburten, Heiraten, Titel, Kriege, Bündnisse, Erbe, Lehnsherr oder Gönner, Vasallen, Haft, Erinnerungen, seit CK3 1.21 auch Sitz und Gesetze der Gesellschaft. Je Zeile `id`, `nr` der Aufnahme, `art`, `datum` (eigenes Datum aus dem Spielstand) oder `zeitraum` (zwischen zwei Aufnahmen), `text`, `figuren`, `quelle`, `wichtig`. Jede Art von Zeile geht durch, außer den technischen Neuladen-Zeilen.
- `aufnahmen/aufnahme-NNNN.json`: je gültiger Aufnahme der Stand zum Spieldatum: die Spielfigur mit allen Werten (seit CK3 1.21 auch Ritus, Sitz, Tributpflichtige, Gesetze und die Art der Bindung an Lehnsherrn oder Gönner; seit Leser 3 des Monitors auch die Art des Vertrags und der Tag, seit dem das Haus des Vorgesetzten ihn hält), Haus und Dynastie, Kriege, Erinnerungen, die Figuren im Blick (Familie, Haus, Lehnsherr, Vasallen, Verbündete, Kriegsparteien, Herrscher der Reiche) und die Titel mit ihrer Art und dem Vermerk „landlos“. `NNNN` ist die Nummer der Aufnahme im Monitor. Dazu `gespeichert_um` (wann das Spiel den Stand geschrieben hat), `gelesen_um`, `lesung` (Format, Version von rakaly und des Lesers im Monitor, Zahl unbekannter Schlüssel und der Abschnitte, die rakaly nur unter Platzhalternamen nennt, Ironman) und `lesestand`.

In den Listen der Figuren und Titel fehlen Felder ohne Wert; ein fehlendes Feld heißt dort „kein Wert im Spielstand“. Bei der Spielfigur bleibt ein fehlender Wert als `null` stehen: „Fehlt“ ist nicht 0.

Eine einmal geschriebene Aufnahme bleibt byte-gleich und erscheint in keinem weiteren Commit. Wird sie nach einem Neuladen verworfen, entfernt das Skript ihre Datei wieder.

**Neuaufbau im Monitor:** Lernt der Monitor dazu, liest er eine Welt aus seinen gesicherten Spielständen neu. Nummern und Lesezeiten der Aufnahmen bleiben dabei, ihr Inhalt und die Chronik ändern sich. Beim nächsten Hochladen schreibt das Skript die betroffenen Dateien neu; der Commit zeigt dann auch ältere Aufnahmen. Die `id` einer Chronikzeile kann nach einem Neuaufbau eine andere sein. Register und Kapitel verweisen deshalb nie auf eine `id` aus `chronik.json`, sondern auf Aufnahme, Spieldatum und Quellennummer.

## Was wegbleibt

- **Privates:** der Block `datei` jeder Aufnahme mit `pfad` (er enthält die Steam-Kontonummer), Dateiname, Größe und Prüfsumme; in `welt.json` das Feld `letzte_datei`; `kampagne.spielername`. `welt.json`, `daten.jsonl` und `chronik.jsonl` selbst kommen nie ins Repo.
- **Verworfene Aufnahmen** nach einem Neuladen, ihre Chronikzeilen und die technischen Neuladen-Zeilen.
- **Verdecktes** führt schon der Monitor nicht: echte Väter, Geheimnisse, Intrigen, Schwangerschaften, geheime Glauben anderer.
- **Neue Felder des Monitors**, bis sie in den Erlaubnislisten von `scripts/monitor_daten.py` stehen. Das Skript nennt sie beim Hochladen.
- **Notizbuch des Spielers** im Monitor. Was der Spieler dort oder in einer Nachricht sagt, geht von Hand als Quelle „Angabe des Spielers“ in die Chronik.

## Drei Sicherungen gegen Privates

1. **Erlaubnislisten** in `scripts/monitor_daten.py`: Veröffentlicht wird nur, was dort als Feld genannt ist.
2. **Muster:** `monitor_daten.privat_funde` und `validate-data.mjs` schlagen an bei Laufwerkspfaden, Benutzer- und Dokumentenordnern, Steam-Ordnern, dem Ordner der Spielstände, Dateinamen von Spielständen, SteamID64 und bei den Schlüsseln `datei`, `pfad`, `letzte_datei`, `spielername`, `sha1`. Die Datenprüfung sucht dazu im ganzen Repo nach Steam-Ordnern mit Kontonummer und nach Dateinamen von Spielständen und meldet Rohdateien des Monitors. `scripts/test-pruefung.mjs` schiebt ihr solche Fälle unter und erwartet jedes Mal einen Fehler.
3. **Genaue Werte:** Das Hochlade-Skript liest Kontonummer, Benutzerordner, Dateinamen und Spielernamen aus dem Monitor und bricht ab, wenn eine fertige Datei einen dieser Werte enthält. Vor dem Commit durchsucht es damit das ganze Repo. Von Hand: `py -3 scripts/privat-pruefen.py`. Die Werte bleiben im Speicher und stehen in keiner Meldung.

Trägt eine Figur im Spiel denselben Namen wie der Spieler, hält die dritte Sicherung den Upload an. Dann entscheidet der Spieler, wie die Figur in der Chronik heißt.

## Bedeutung und Grenzen

- **Jeder Wert hat seinen Zeitpunkt:** Alles gehört zum Spieldatum seiner Aufnahme. Ein eigenes Datum haben Geburt, Tod, Kriegsbeginn und Erinnerungen; alles andere trägt den Zeitraum zwischen zwei Aufnahmen. Seit Leser 3 datiert der Monitor auch den Wechsel des Lehnsherrn oder Gönners aus dem Vertrag und bei Kaufleuten damit den Umzug der Gesellschaft; die Zeile nennt dann als Quelle „Vertrag mit dem Gönner“.
- **Wer zum ersten Mal auftaucht, ist nicht unbedingt neu:** Die Chronik des Monitors unterscheidet „Geburt“ und „Neu im Blick“, „Krieg begonnen“ und „Krieg jetzt im Blick“.
- **Ursachen fehlen:** Der Spielstand nennt weder Ereignistexte noch Entscheidungen. Eine Todesursache steht nur da, wenn der Spielstand sie nennt.
- **Gelesen ist nicht bestätigt:** `lesestand` sagt, ob die Spielversion ohne Lücken gelesen und ob sie im Spiel verglichen ist. Zahlen einer Version gelten als belegt, sobald der Spieler fünf Werte im Spiel verglichen hat; bis dahin sind sie vorläufig. Der Vermerk steht in jeder Aufnahme so, wie die Version beim Lesen stand: Nach einem Vergleich tragen ihn erst die späteren Aufnahmen, die früheren nach dem nächsten Neuaufbau. `scripts/fakten.py` nimmt deshalb den jüngsten Vermerk zur Spielversion. CK3 1.21.0 führt der Monitor seit dem 17.11.2026 als im Spiel bestätigt (im ersten Lauf ab der Aufnahme Nr. 14). Was rakaly nur unter Platzhalternamen nennt, liest der Monitor nicht; dafür gilt keine Bestätigung.
- **Namen** kommen aus den deutschen Sprachdateien des installierten Spiels und sind Beschriftung. Verglichen wird über Kennungen.
