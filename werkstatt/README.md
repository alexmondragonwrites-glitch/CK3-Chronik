# Werkstatt – gemeinsamer Arbeitsbereich für Claude und Codex

Hier stimmen sich die KI-Sitzungen ab, die an den Chroniken arbeiten. Die Chroniken selbst liegen unter `saves/<lauf>/`. Die Werkstatt hält fest, wer gerade woran arbeitet, wie weit ein Lauf erzählt ist und welche Aufnahmen bereitliegen.

**Öffentlich:** Das Repo ist öffentlich und wird als GitHub Pages ausgeliefert. Alles in `werkstatt/` ist im Netz lesbar. Keine Zugangsdaten, Schlüssel, lokalen Pfade, Kontonummern, Dateinamen von Spielständen oder privaten Dateien ablegen, und nie den Spielernamen aus dem Spielstand.

## Was wo liegt

| Datei | Zweck | Wer schreibt |
|---|---|---|
| `AUFGABEN.md` | Tafel mit In Arbeit, Zur Prüfung, Offen, Erledigt. Wer etwas anfängt, trägt sich zuerst hier ein. | alle Sitzungen |
| `LOG.md` | Übergaben und Reviews, neueste oben. Nur ergänzen, nichts umschreiben. | alle Sitzungen |
| `erster-lauf/STAND.md` | Wie weit der erste Lauf erzählt ist, nächste freie Quellennummer, Stand der Aufnahmen, Bücher, Stimmen und Formen des Tagebuchs. | wer ein Kapitel abschließt |
| `erster-lauf/fakten/kapitel-N.md` | Faktenblatt je Kapitel aus den Aufnahmen des Paradox-Monitors, für den Zeitraum des Kapitels. Erzeugt von einem Skript, nicht von Hand ändern. | Skript |
| `erster-lauf/figuren/` | Profil je Erbe aus dem Spielstand, bis der Spieler etwas ergänzt. | wer ein Buch beginnt |
| `../lore/joshua-von-silberfurt.md` | Dossier der ersten Spielfigur: verbindlicher Kanon des Spielers. Das Tagebuch hält sich daran; Offenes bleibt offen. | Spieler |

## Ablauf einer Sitzung

1. **Aktualisieren:** `git fetch origin` und `git merge --ff-only origin/main`. Andere Sitzungen schieben parallel.
2. **Lesen:** `AUFGABEN.md`, die obersten Einträge in `LOG.md`, den `STAND.md` des Laufs.
3. **Eintragen:** Aufgabe unter „In Arbeit“ mit Wer, Datum und Dateien. Solange dort jemand für eine Datei eingetragen ist, ändert niemand sonst sie. `chronik.html` und `data/events.json` eines Laufs gelten zusammen als eine Einheit.
4. **Arbeiten** nach den Regeln des Laufs (`docs/<LAUF>.md`).
5. **Prüfen:** mindestens `node scripts/validate-data.mjs`; wer den Paradox-Monitor neben dem Repo hat, dazu `py -3 scripts/privat-pruefen.py`.
6. **Abschließen:** Aufgabe nach „Erledigt“ (mit Commit) oder nach „Zur Prüfung“, `STAND.md` nachziehen, Übergabe oben in `LOG.md`.
7. **Hochladen nur mit Freigabe des Spielers.** Vor dem Push erneut `git fetch`; ist `origin/main` weiter, zusammenführen. Kein `--force`, keine fremden Commits umschreiben.

## Regeln für alle

- **Wortlaut:** Veröffentlichte Kapitel nicht umschreiben. Ausnahme: ein Fehler. Dann knapp korrigieren und unter „Korrekturen“ in der Chronik mit Datum und Grund vermerken.
- **Register:** `data/events.json` ist append-only. Einträge nicht löschen; Fehler bekommen ein Feld `correction` mit `date` und `note`. Ins Register kommt nur Belegtes (`fakt`) und Abgeleitetes (`rekonstruktion`); Erzähltes steht im Tagebuch.
- **Zahlen** nur aus Aufnahmen, Faktenblättern oder Angaben des Spielers. Fehlt etwas, bleibt es offen und kommt unter „Offene Fragen“.
- **Zeit:** Crusader Kings zählt nach dem Kalender. Register und Kapitel tragen das Spieldatum, daneben steht der Tag der Aufnahme. Ohne eigenes Datum im Spielstand steht der Zeitraum zwischen zwei Aufnahmen.
- **Ursachen:** Der Spielstand nennt weder Ereignistexte noch Entscheidungen noch Gründe. Niemand erfindet sie. Was der Spieler dazu sagt, geht als Quelle „Angabe des Spielers“ ein.
- **Spielerwissen:** Verdecktes bleibt draußen: echte Väter, Geheimnisse, Intrigen, Schwangerschaften, geheime Glauben anderer.
- **Neuladen:** Springt das Spieldatum zurück, gehören die Aufnahmen dahinter zu einem verworfenen Abschnitt. Sie kommen weder in die Chronik noch in die veröffentlichten Aufnahmen.
- **Namen:** Die Menschen des Spielstands tragen ihre Namen aus dem Spiel. Erfundene Menschen stehen nur im Tagebuch, nie im Register.
- **Quellen:** Nummern (Q1, Q2, …) vergibt, wer ein Kapitel schreibt. Die nächste freie Nummer steht im `STAND.md` des Laufs.
- **Bilder** unter `saves/<lauf>/images/`, nur eigene Zeichnungen; keine Spielgrafik (Porträts, Wappen, Karte, Artwork). KI-Bilder als solche kennzeichnen.
- **Keine Zukunft:** Keine Sitzung plant, was in der Partie passieren wird. Der Spieler spielt, die Chronik folgt.
- **Läufe getrennt:** Nichts aus einem Lauf in einen anderen übernehmen.

## Wer was kann

- **Claude** (Claude Code auf dem Rechner des Spielers) kommt an den Paradox-Monitor: lädt Aufnahmen hoch (`scripts/publish-monitor.py`), erzeugt Faktenblätter, schreibt Kapitel.
- **Codex** hat in der Regel nur dieses Repo. Prüft Kapitel gegen Faktenblätter, Aufnahmen und Register (Zahlen, Spieldaten, Textarten, Regeln), schreibt auf Absprache auch Kapitel. Aufnahmen erzeugt Codex nicht selbst; fehlt ein Faktenblatt, kommt das als Aufgabe für Claude auf die Tafel.

## Review-Format

Wer prüft, schreibt in `LOG.md` einen Eintrag „Review“ mit Fundstellen: Datei, Abschnitt, was steht, was die Quelle sagt, Vorschlag. Ändern darf die Sitzung, die die Datei unter „In Arbeit“ hält, oder nach Absprache die prüfende.
