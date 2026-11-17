# Erster Lauf

Erste Partie der CK3-Chronik, begonnen am 17.11.2026 mit Crusader Kings III 1.21 „Florin“ und der Erweiterung Silk & Silver. Erzählt wird sie im Tagebuch der Spielfigur; die erste ist Joshua von Silberfurt, ein Kaufmann, im Spiel ab dem 1.1.867. „Erster Lauf“ ist ein Arbeitstitel, bis der Spieler den Namen bestätigt. Die Entscheidungen des Briefings stehen in `BRIEFING.md`. Wie weit erzählt ist: `werkstatt/erster-lauf/STAND.md` und `werkstatt/AUFGABEN.md`.

## Wo was liegt

| Datei | Inhalt |
|---|---|
| `saves/erster-lauf/chronik.html` | Die Chronik: Titelblatt, die erste Spielfigur (Figurenkanon), Steckbrief der Partie, Register, Bücher und Kapitel, Haus und Titel, offene Fragen, Quellen, Korrekturen. Handgeschrieben. |
| `lore/joshua-von-silberfurt.md` | Dossier des Spielers für die erste Spielfigur, verbindlicher Kanon, dazu „Ergänzungen des Spielers“. Ändert nur der Spieler oder eine Sitzung auf seinen Wunsch. |
| `saves/erster-lauf/data/` | `meta.json`, `manifest.json`, `events.json` (Register, nur anhängen), später `monitor/` (Aufnahmen, von `scripts/publish-monitor.py`). |
| `werkstatt/erster-lauf/` | `STAND.md`, `fakten/` (Faktenblatt je Kapitel), `figuren/` (Profile der Erben aus dem Spielstand). |

## Bücher und Kapitel

1. **Es schreibt die Spielfigur** in der Ich-Form. Jede Spielfigur hat ein eigenes Buch. Mit dem Herrscherwechsel schließt es, und der Erbe beginnt seines mit eigener Stimme. Den Wechsel hält das Register fest; ein Tod steht dort mit Datum, die Ursache nur so, wie der Spielstand sie nennt.
2. **Kapitel schließen mit einem Einschnitt**, zum Beispiel: ein Krieg ist beendet; ein Titel ist erlangt oder verloren; eine Heirat oder die Geburt des Erben; ein neuer Lehnsherr; bei Kaufleuten ein Schritt der Familie nach oben.
3. **Claude schlägt den Einschnitt aus dem Faktenblatt vor, der Spieler bestätigt ihn.** Will er ein Kapitel früher schließen, gilt sein Wort.
4. **Kapitel zählen über den ganzen Lauf fortlaufend** in römischen Ziffern, auch über die Grenze eines Buches hinweg.
5. **Stichtag:** Jedes Kapitel nennt das Spieldatum der letzten verwendeten Aufnahme und den Tag dieser Aufnahme.
6. **Aufbau:** ein knapper Bericht (Belegt) mit Spieldatum und Quelle, Tagebucheinträge, Abgeleitetes als Randnotiz. Die Formen wechseln: Brief, Liste, Abschrift einer Urkunde, Gebet, Rechnung.

Das Gerüst im HTML, mit den Bausteinen aus `musterblatt.html`:

```html
<section class="hs-buch" id="buch-1" aria-labelledby="buch-1-titel">
  <header class="hs-buch-kopf">
    <p class="hs-buch-nr">Erstes Buch</p>
    <h3 id="buch-1-titel">Name der Spielfigur</h3>
    <p class="hs-buch-zeit">von … bis …</p>
  </header>
  <article class="hs-kapitel" id="kapitel-1" data-spieldatum-bis="JJJJ-MM-TT" aria-labelledby="kapitel-1-titel">
    <header class="hs-kapitel-kopf">
      <p class="hs-kapitel-nr">Kapitel I</p>
      <h4 id="kapitel-1-titel">Titel</h4>
      <p class="hs-kapitel-zeit">Spieldatum von bis · aufgenommen am …</p>
      <p class="hs-kapitel-einschnitt">Schließt mit …</p>
      <div class="hs-leiste" aria-hidden="true"></div>
    </header>
    <div class="hs-bericht"><span class="hs-etikett">Belegt</span> … <p class="hs-quelle">…</p></div>
    <aside class="hs-randnotiz"><span class="hs-etikett">Abgeleitet</span> …</aside>
    <div class="hs-tagebuch"><span class="hs-etikett">Tagebuch</span>
      <section class="hs-eintrag"><h5 class="hs-rubrik">Datumszeile</h5><p>…</p></section>
    </div>
  </article>
</section>
```

Mit dem ersten Buch kommt ein Eintrag in `meta.json` unter `buecher` dazu (Nummer, Kennung und Name der Spielfigur, Spieldatum von und bis). Ein Eintrag mit eigener Form trägt `hs-eintrag--schlicht`; dann entfällt die Schmuckinitiale.

## Tagebuch und Kanon

1. **Dossier und Spielstand:** Das Dossier erzählt die Zeit vor Spielbeginn, die Aufnahmen die Zeit danach. Was das Spiel an Namen und Werten zeigt, gilt als bestätigt. Weichen Dossier und Spielstand voneinander ab, entscheidet der Spieler.
2. **Offenes bleibt offen.** Das Dossier nennt unter „Offen“, was es nicht festlegt. Das Tagebuch füllt diese Stellen nicht.
3. **Was die Figur über Familie, Titel, Kriege, Bündnisse, Gold und Ansehen schreibt, folgt den Aufnahmen.** Gedanken, Begegnungen und Wetter sind Erzählung.
4. **Namen:** Die Menschen des Spielstands tragen ihre Namen aus dem Spiel. Erfundene Menschen stehen nur im Tagebuch, nie im Register.
5. **Erben:** Ihr Profil entsteht aus dem Spielstand (Eigenschaften, Erziehung, Fertigkeiten, Familie, Glaube, Erinnerungen) in `werkstatt/erster-lauf/figuren/`. Was der Spieler ergänzt, wandert nach `lore/` und gilt dann als Kanon.
6. **Schreibweise** nach `docs/SCHREIBSTIL.md`.
7. **Das Dossier auf der Seite:** Der Abschnitt „Die erste Spielfigur“ gibt das Dossier im Wortlaut des Spielers wieder (Quelle Q2), vom Titel bis vor den Abschnitt „Offen“. Der Kasten trägt `data-kanon="lore/joshua-von-silberfurt.md"`; die Datenprüfung vergleicht jeden Absatz mit der Datei und meldet jede Abweichung. Wer das Dossier fortschreibt, zieht die Seite nach. Was das Dossier offen lässt, steht unter „Offene Fragen“.
8. **Der Ort:** Das Dossier nennt Grüningen. Im Spiel liegt der Sitz der Gesellschaft an anderen Orten. Der Spieler am 17.11.2026: „wir gehen mit der reise nach frankfurt“ (Quelle Q4). Vom Spieler am selben Abend bestätigt („passt“): Die Chronik erzählt den Zug nach Frankfurt, Grüningen bleibt Joshuas Herkunft aus dem Dossier, und das Register nennt die Sitze so, wie die Aufnahmen sie zeigen (Ulm am 1.1.867, Frankfurt seit dem Frühjahr 867). Das Dossier bleibt dabei unverändert; der Wortlaut steht dort unter „Ergänzungen des Spielers“.

## Regeln aus dem Briefing

- **Belegt, Abgeleitet und Tagebuch trennen.** Zahlen nur aus Aufnahmen des Monitors oder aus Angaben des Spielers.
- **Zeit:** Register und Kapitel tragen das Spieldatum (etwa 13.2.875), daneben steht der Tag der Aufnahme. Ein eigenes Datum haben Geburt, Tod, Kriegsbeginn und Erinnerungen; alles andere trägt den Zeitraum zwischen zwei Aufnahmen (`zeitraum` im Register).
- **Was der Spielstand verschweigt:** Ereignistexte, Entscheidungen und Gründe. Das Tagebuch erfindet dafür keine Ursachen. Was der Spieler dazu sagt (in einer Nachricht oder im Notizbuch des Monitors), geht als Quelle „Angabe des Spielers“ ein.
- **Spielerwissen:** Verdecktes bleibt draußen wie im Monitor: echte Väter, Geheimnisse, Intrigen, Schwangerschaften, geheime Glauben anderer.
- **Neuladen wird nicht erzählt.** Keine Sitzung plant die Zukunft der Partie: Der Spieler spielt, die Chronik folgt.
- **Veröffentlichten Wortlaut** nur zur Korrektur eines Fehlers ändern, mit Eintrag unter „Korrekturen“. `data/events.json` ist append-only.
- **Bilder:** Porträts, Wappen, Karte und Artwork aus dem Spiel kommen nicht auf die Seite. Eigene Zeichnungen aus den Daten sind erlaubt.
- **Hochladen** nur mit Freigabe des Spielers („Ja, hochladen“).

## Lesestand von Version 1.21

Der Monitor liest binäre Spielstände mit dem Werkzeug rakaly. Am 17.11.2026 nennt noch keine Version von rakaly CK3 1.21. Zahlen aus 1.21 gelten als belegt, sobald der Spieler fünf Werte im Spiel verglichen hat; den Stand führt der Monitor. Bis dahin tragen die Aufnahmen den Lesestand „ungeprüft“, und ein Kapitel wartet.

## Erscheinungsbild

„Handschrift“ nach `assets/handschrift.css`: Pergament, braunschwarze Tinte, rote Rubriken, Schmuckinitialen, Blattranke. Farbe und Ornament des Laufs stehen noch aus: Den Vorschlag für die Farbe liefert das Wappen des Hauses, der Spieler bestätigt; bis dahin gilt die Vorgabe (Blau, Ranke). Die Farben zum Ansehen: `musterblatt.html`. Eintragen an `<html>` der Chronik (`data-farbe`, `data-stil`) und in `meta.json` (`farbe`, `stil`).

## Paradox-Monitor

Die Welt des Laufs im Monitor ist `ck3:a2be71f2-d985-4ba1-b9d7-05841d0295fc` („von Silberfurt ab 867“), eingetragen in `data/monitor-sources.json` und `meta.json`. Aufnahmen sind noch keine veröffentlicht; der erste Lauf von `WEBSITE_AKTUALISIEREN.bat` im Monitor oder von `py -3 scripts/publish-monitor.py --save erster-lauf` schreibt sie und stellt das Manifest um. Beginnt der Spieler die Partie neu, stellt eine Sitzung die Kennung mit `--welt` um. Einzelheiten: `docs/MONITOR.md`.

## Ablauf für ein Kapitel

1. Aufnahmen hochladen oder lokal bauen (`--no-push`), Faktenblatt für den Zeitraum erzeugen (`werkstatt/erster-lauf/fakten/kapitel-N.md`).
2. Einschnitt vorschlagen, Bestätigung des Spielers abwarten.
3. Kapitel in `chronik.html` schreiben, Register in `events.json` anhängen, Quellen ergänzen, `STAND.md` nachziehen.
4. Prüfen: `node scripts/validate-data.mjs`, `py -3 scripts/privat-pruefen.py`, Vorschau im Browser (hell, dunkel, Handy).
5. Hochladen nach Freigabe.
