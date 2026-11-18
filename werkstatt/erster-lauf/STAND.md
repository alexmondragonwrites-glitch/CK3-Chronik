# Erster Lauf · Stand

Stand 18.11.2026 (Claude). **Kapitel I „Die Reise nach Frankfurt“ ist online seit dem 17.11.2026** (`574162b`); der Spieler hat es in der Vorschau bestätigt („Passt so“) und freigegeben („Ja, hochladen“). **Seit dem 18.11.2026 ist die berichtigte Fassung online:** Sie trägt die Reise nach Würzburg nach, vom Spieler beauftragt („Ja, nachtragen“) und freigegeben („Ja, hochladen“). Erzählt ist bis zum Spieldatum 2.4.867. Nächste freie Quellennummer: **Q9** (Q1 das Briefing, Q2 das Dossier, Q3 der Paradox-Monitor mit der ersten Aufnahme, Q4 die Angabe des Spielers zum Ort, Q5 die Aufnahmen Nr. 1 und 2 mit dem Faktenblatt, Q6 die Angaben des Spielers zu Kapitel I, Q7 der Spielstand vom 2.4.867 für Vertrag und Familie Wartenberg, Q8 dieselben Aufnahmen neu gelesen für Hof, Aufträge und Reise). Nächste freie Registernummer: `erster-lauf-0017`.

## In Arbeit seit dem 18.11.2026: Leser 4 und Kapitel II

1. **Erlaubnislisten für Leser 4:** in `scripts/monitor_daten.py` eingetragen (`aufenthalt`, `reise`, `am_ort`, `auftraege`, `hof`, Eigenschaften der Figuren, `titel.erwerb`, `kriege.umfeld`, Unternehmungen mit Protokoll, Umfeld des Sitzes). `scripts/fakten.py` zeigt Aufenthalt, Reise, Aufträge, Hof, „am selben Ort“, das Umfeld und Unternehmungen. Die 22 vorhandenen Tests laufen. **Noch offen:** eigene Tests für die neuen Felder und `docs/MONITOR.md`.
2. **Kapitel II:** Schnitt vom Spieler entschieden („Ja, so schließen“): Es schließt am Stichtag 2.9.869 (Geburt Elisabeths, Rückkehr aus Mainz), von Aufnahme Nr. 2 bis Nr. 12. Das Faktenblatt entsteht mit `py -3 scripts/fakten.py --save erster-lauf --kapitel 2 --von 0867-04-02 --bis 0869-09-02` und liegt lokal. **Noch nicht begonnen:** Beiblatt zu Kapitel II, Bericht, Tagebuch, Register, Quellen, `meta.json`. Den Stoff nennt der Abschnitt „Stoff für Kapitel II“ unten.

## Figur und Kanon

- **Erste Spielfigur:** Joshua von Silberfurt. Der Spieler hat ihn am 17.11.2026 als erste Figur der Chronik benannt und das Dossier dazu gegeben.
- **Dossier:** `lore/joshua-von-silberfurt.md`, verbindlicher Kanon. Die Datei schreibt nur die Hauptsitzung fort. Die Seite gibt das Dossier im Wortlaut wieder (Abschnitt „Die erste Spielfigur“, `data-kanon`); die Datenprüfung vergleicht den Wortlaut. Was das Dossier offen lässt, steht auf der Seite unter „Offene Fragen“.
- **Ort, entschieden (Angabe des Spielers vom 17.11.2026):** „wir gehen mit der reise nach frankfurt“. Anlass: Das Dossier nennt Grüningen; nach den Aufnahmen begann die Gesellschaft im Spiel in Ulm und sitzt seit dem 30.1.867 in Frankfurt. Vom Spieler am selben Abend bestätigt („passt“): Die Chronik erzählt den Zug nach Frankfurt. Grüningen bleibt Joshuas Herkunft aus dem Dossier. Das Register nennt die Sitze so, wie die Aufnahmen sie zeigen. Der Wortlaut steht auch im Dossier unter „Ergänzungen des Spielers“.
- **Name des Laufs:** „Erster Lauf“ ist Arbeitstitel, bis der Spieler den Namen bestätigt (Vorschlag an ihn: „Haus von Silberfurt · Erster Lauf“).
- **Farbe und Ornament:** Vorgabe (Blau, Ranke), bis der Spieler am Musterblatt gewählt hat.

## Partie

- Begonnen am 17.11.2026 mit Crusader Kings III 1.21 „Florin“ und Silk & Silver; im Spiel ab dem 1.1.867.
- **Weltkennung:** `ck3:a2be71f2-d985-4ba1-b9d7-05841d0295fc`, im Monitor „von Silberfurt ab 867 (Meister Joshua)“. Eingetragen in `data/monitor-sources.json` und `meta.json`.
- **Lesestand:** bestätigt. Der Spieler hat am 17.11.2026 die Werte vom Stand 2.12.869 im Spiel verglichen („Ja, stimmen“): Gold, Einkommen, Prestige, Frömmigkeit, Einfluss, Stress, Sitz, Gönner und Erbe. Seit dem Neuaufbau der Welt tragen alle Aufnahmen den Vermerk „bestätigt“. rakaly kennt Version 1.21 noch nicht und nennt sieben Abschnitte nur unter Platzhalternamen (nach der Hauptsitzung Handel und Bezirke); was dort steht, ist weder gelesen noch bestätigt.
- **Leser 4 seit dem 18.11.2026:** Der Monitor liest Aufenthalt, Reise, Aufträge, Hof und Ämter, wer am selben Ort ist, Unternehmungen, das Umfeld des Sitzes, den Erwerb von Titeln und die Eigenschaften aller Figuren. Am 18.11.2026 lagen 35 gültige Aufnahmen vor, bis zum Spieldatum 16.2.875.
- **Erlaubnislisten:** Die neuen Felder stehen seit dem 18.11.2026 darin (`figuren.eigenschaften`, `kriege.umfeld`, `umfeld`, `unternehmungen`, `spieler.am_ort`, `spieler.aufenthalt`, `spieler.auftraege`, `spieler.hof`, `spieler.reise`, `titel.erwerb`). Nach der Hauptsitzung enthalten sie nur Spielinhalt; die Bestandteile von Reise, Aufträgen und Hof gehen so durch, wie der Monitor sie führt. Die Chronik des Monitors (Arten `reise`, `auftrag`, `am_ort`, `hof`, `umfeld`, `unternehmung`) geht ebenfalls durch.
- **Aufnahmen online:** keine. Ob sie auf die Seite sollen, hat der Spieler noch nicht gesagt.
- Probeläufe des Hochlade-Skripts mit dieser Welt (Ausgabe außerhalb des Repos) liefen am 18.11.2026 ohne Fund von Privatem.

## Erzählt

### Erstes Buch: Joshua von Silberfurt (seit dem 1.1.867)

**Kapitel I · Die Reise nach Frankfurt** · Spieldatum 1.1.867 bis 2.4.867 · Stichtag Aufnahme Nr. 2, gespeichert am 17.11.2026 um 19:08 Uhr · Einschnitt vom Spieler bestätigt („Ja, so schließen“): die Ankunft in Frankfurt.

Online steht seit dem 18.11.2026 die **berichtigte Fassung**, die das Folgende beschreibt; die erste Fassung steht im Verlauf des Repos (`574162b`).

- **Bericht:** Beginn in Ulm (Gönner Welf, Zweck Händler, 50 Gold, Einkommen 0,70; am Hof Udalrich und Walpurga; am selben Ort Nikolaus), Gründung am 2.1.867, Auftrag „Warenlage kennenlernen“ am 24.1., Vertrag mit Liutbert und Sitz Frankfurt am 30.1., Auftrag „Zollaushandlung“ und Abreise nach Würzburg am 5.2., Heirat mit Cothilda (Wartenberg) am 16.2., Ankunft in Würzburg am 17.2., Bündnis mit Nikolaus, Zweck Kunsthandwerker. Am Stichtag: Joshua in Würzburg, Rückkehr geplant für den 17.4.867; Cothilda (Leibarzt) und Walpurga (Partner) in Frankfurt; 32,74 Gold, Einkommen 1,24.
- **Randnotiz (Abgeleitet):** sechs Tage zwischen Vertrag und Abreise; zwölf Tage Reise; am Tag der Heirat seit elf Tagen unterwegs; am Stichtag seit 44 Tagen in Würzburg; 17,26 Gold weniger, Einkommen 0,54 höher.
- **Register:** `erster-lauf-0001` bis `-0016`. Die Einträge `-0003` und `-0004` (Sitz, Gönner) tragen noch den Zeitraum, wie die Aufnahmen ihn am 17.11. zeigten; den Tag nennt `-0005` als abgeleitet.
- **Tagebuch, elf Einträge:** Ulm am Neujahrstag; Abschrift aus dem Buch der Gesellschaft vom 2. Januar; Ulm am 9. Januar (Entschluss für Frankfurt); unterwegs am 21. Januar; Frankfurt am 30. Januar (Ankunft, Vertrag mit Liutbert); Frankfurt am 3. Februar (Begegnung mit Cothilda an der Marktwaage); **Frankfurt am 5. Februar (Auftrag von Udalrich, Aufbruch nach Würzburg)**; **unterwegs am 16. Februar (Heirat)**; **Würzburg am 17. Februar (Ankunft)**; **Würzburg am 12. März (neuer Zweck)**; **Würzburg am 2. April (Rechnung, Rückreise angesetzt)**. Fett: neu oder berichtigt.
- **Erzählt, also ohne Beleg im Spielstand** (für spätere Kapitel merken): das Haus der Gesellschaft liegt nahe am Markt in Frankfurt, unten Lager und Schreibstube, oben die Wohnung; die Reise von Ulm mit einem gemieteten Wagen und einem Fuhrmann, Aufbruch am 11. Januar; Joshua führt neben dem Tagebuch das „Buch der Gesellschaft“ und hat es auf Reisen bei sich; er trägt hinten im Heft ein, was an den Orten gewogen und gehandelt wird; die Begegnung an der Marktwaage mit dem Wäger und dem Jungen mit dem Korb; nach Würzburg reist er mit leichtem Gepäck; dort eine Kammer in einer Herberge am Fluss; unterwegs hat er Zollstellen gezählt; am 12. März geht ein Brief an Walpurga wegen des neuen Zwecks. Die Tage der Einträge vom 9. und 21. Januar, 3. Februar und 12. März sind erzählt.
- **Bewusst offen gelassen:** wo und wie die Ehe am 16.2.867 geschlossen wurde (Frage liegt beim Spieler); warum Cothilda in Frankfurt war; ob Nikolaus bei der Heirat dabei war; ob Joshua Ludwig dem Jüngeren oder Yefet (Ben Asher) begegnet ist; warum Walpurga für Würzburg verhindert war; wie die Zollaushandlung steht; was die Werkstätten fertigen und womit die Gesellschaft handelt (Handel liest der Monitor noch nicht); wofür das Gold ausgegeben wurde; ob Joshuas Eltern leben.
- **Menschen des Spielstands im Tagebuch:** Welf, Udalrich, Liutbert, Cothilda, Nikolaus, Walpurga, Ludwig der Jüngere. Im Bericht außerdem Gudrun und Yefet (Ben Asher).

## Offen zu Kapitel I

- **Die Heirat am 16.2.867:** entschieden. Der Spieler am 18.11.2026 auf die Frage, wie das Tagebuch sie erzählt: „Nur den Tag nennen“. Wo und wie die Ehe geschlossen wurde, bleibt offen und wird auch später nicht nachgetragen, solange er nichts anderes sagt.
- **Liutberts Titel:** In den Aufnahmen heißt er nur „Mainz“ (Schlüssel `d_et_mainz`, ein Kirchentitel ohne Stufenname). „Erzbistum“ steht deshalb nirgends im Kapitel; das Tagebuch nennt ihn „Liutbert von Mainz, den geistlichen Herrn“.
- **Ludwig der Jüngere:** Sein Haupttitel heißt in der Aufnahme „Westfranken“ (Herzogtum). Das Kapitel nennt ihn ohne Rang.

## Stoff für Kapitel II

Alles nach dem 2.4.867, nach den Meldungen der Hauptsitzung vom 18.11.2026 (vor dem Schreiben am Faktenblatt prüfen):

- Die Reise endet nicht am Stichtag: Auch die Stände vom 14.6., 2.9. und 2.12.867 und vom 2.3.868 zeigen Joshua in Würzburg, die Reise als „paused“, die Zollaushandlung als angenommen. Zurück in Frankfurt ist er vor dem 10.5.868.
- Cothilda als Erbin (zwischen dem 2.4. und dem 14.6.867). „Warenlage kennenlernen“ ist am 2.9.867 nicht mehr offen. Am 1.12.867 nimmt er „Investitionsanregung“ an; Walpurga steht am 2.12.867 in Ulm.
- 10.5.868 Reise nach Mainz mit Cothilda, Ankunft am 13.5., „Umgang mit Gönner“ angenommen; am selben Ort Liutbert.
- 22.6.869 Geburt der Tochter Elisabeth, die seither Erbin ist (die Hauptsitzung nennt sie als möglichen Schluss).
- Später: Festmahl in Frankfurt (Einladung 7.3.870, Beginn 4.8.870, mit Protokoll), Geburt Amalberga am 17.7.870, Freundschaft mit Liutbert am 22.8.870, Frankfurt an Ludwig den Deutschen am 21.11.870, Krieg ab dem 11.5.871, Geburt Nikolaus am 10.9.871, Reise nach Ulm im November 871, Geburt Johann am 29.12.873, Tod Ludwigs des Deutschen am 22.2.874.

Den Einschnitt bestätigt der Spieler.

## Angaben des Spielers

Wortlaut und Lesart stehen im Dossier unter „Ergänzungen des Spielers“ und im Beiblatt `fakten/kapitel-1-beiblatt.md`.

- Warum Frankfurt? Frankfurt bringt die meisten Gewinne.
- Warum Kunsthandwerker statt Händler? Im Spiel ein Versehen des Spielers. Für die Chronik gilt der Grund, den er bestätigt hat („Ja, passt“): Joshua will für Qualität einstehen können; die Gesellschaft soll verkaufen, was ihre eigenen Werkstätten fertigen.
- Wie kam es zur Ehe mit Cothilda? Die beiden haben sich in Frankfurt kennengelernt.
- Soll Kapitel I die Reise nach Würzburg nachtragen? „Ja, nachtragen“ (18.11.2026, in der Hauptsitzung).
- Wie soll das Tagebuch die Heirat am 16.2.867 erzählen? „Nur den Tag nennen“ (18.11.2026).

## Stimmen und Formen

- **Joshua (Erstes Buch):** schreibt ruhig und genau, in der Ich-Form, meist im Perfekt. Er nennt Orte, Namen und Summen, zählt nach und liest gegen. Gefühle stehen selten da; man merkt sie an dem, was er aufschreibt. Anhalt im Dossier: Klosterschule, Freude an Handschriften, Fleiß bis in die Nacht, die Sätze von Vater und Mutter, das Vertrauen als Grundlage des Handels, der Wahlspruch.
- **Formen bisher:** Tagebucheintrag mit Datumszeile (Ort und Tag), Abschrift aus dem Buch der Gesellschaft (Urkunde), Rechnung. Noch unbenutzt: Brief, Liste, Gebet.
- **Bezugszeile:** Unter dem Etikett „Tagebuch“ steht in `hs-bezug`, zu welchen Aufnahmen erzählt wird und was Erzählung ist.
- **Berichtigungen:** Ein Fehler im veröffentlichten Kapitel wird im Text berichtigt und unter „Korrekturen“ mit Datum, Grund und Verweis auf die frühere Fassung ausgewiesen; das Register wächst nur.
