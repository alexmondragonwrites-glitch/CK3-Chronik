# Erster Lauf · Stand

Stand 17.11.2026, abends (Claude). Das Gerüst ist online seit `afde4c9`. **Kapitel I „Die Reise nach Frankfurt“ ist online seit dem 17.11.2026**; der Spieler hat es in der Vorschau bestätigt („Passt so“) und freigegeben („Ja, hochladen“). Erzählt ist damit bis zum Spieldatum 2.4.867. Nächste freie Quellennummer: **Q8** (Q1 das Briefing mit den Angaben des Spielers, Q2 das Dossier, Q3 der Paradox-Monitor mit der ersten Aufnahme, Q4 die Angabe des Spielers zum Ort, Q5 die Aufnahmen Nr. 1 und 2 mit dem Faktenblatt, Q6 die Angaben des Spielers zu Kapitel I, Q7 der Spielstand vom 2.4.867, nachgelesen für Vertrag und Familie Wartenberg). Nächste freie Registernummer: `erster-lauf-0010`.

## Figur und Kanon

- **Erste Spielfigur:** Joshua von Silberfurt. Der Spieler hat ihn am 17.11.2026 als erste Figur der Chronik benannt und das Dossier dazu gegeben.
- **Dossier:** `lore/joshua-von-silberfurt.md`, verbindlicher Kanon. Die Datei schreibt nur die Hauptsitzung fort. Die Seite gibt das Dossier im Wortlaut wieder (Abschnitt „Die erste Spielfigur“, `data-kanon`); die Datenprüfung vergleicht den Wortlaut. Was das Dossier offen lässt, steht auf der Seite unter „Offene Fragen“.
- **Ort, entschieden (Angabe des Spielers vom 17.11.2026):** „wir gehen mit der reise nach frankfurt“. Anlass: Das Dossier nennt Grüningen; nach den Aufnahmen begann die Gesellschaft im Spiel in Ulm und sitzt seit dem Frühjahr 867 in Frankfurt. Vom Spieler am selben Abend bestätigt („passt“): Die Chronik erzählt den Zug nach Frankfurt. Grüningen bleibt Joshuas Herkunft aus dem Dossier. Das Register nennt die Sitze so, wie die Aufnahmen sie zeigen: Ulm am 1.1.867, Frankfurt seit dem Frühjahr 867. Der Wortlaut steht auch im Dossier unter „Ergänzungen des Spielers“. Auf der Seite: ein Satz unter dem Dossier, die Quelle Q4 und der Bericht zu Kapitel I.
- **Name des Laufs:** „Erster Lauf“ ist Arbeitstitel, bis der Spieler den Namen bestätigt (Vorschlag an ihn: „Haus von Silberfurt · Erster Lauf“).
- **Farbe und Ornament:** Vorgabe (Blau, Ranke), bis der Spieler am Musterblatt gewählt hat.

## Partie

- Begonnen am 17.11.2026 mit Crusader Kings III 1.21 „Florin“ und Silk & Silver; im Spiel ab dem 1.1.867.
- **Weltkennung:** `ck3:a2be71f2-d985-4ba1-b9d7-05841d0295fc`, im Monitor „von Silberfurt ab 867 (Meister Joshua)“. Eingetragen in `data/monitor-sources.json` und `meta.json`.
- **Lesestand:** bestätigt. Der Monitor vermerkt seit der Aufnahme Nr. 14: „Version 1.21.0: am 2026-11-17 im Spiel bestätigt.“ Der Spieler hat die Werte vom Stand 2.12.869 im Spiel verglichen („Ja, stimmen“): Gold, Einkommen, Prestige, Frömmigkeit, Einfluss, Stress, Sitz, Gönner und Erbe. Die Aufnahmen Nr. 1 bis 13 tragen den Vermerk „ungeprüft“ vom Zeitpunkt des Lesens, bis der Monitor die Welt neu aufbaut. rakaly kennt Version 1.21 noch nicht und nennt sieben Abschnitte nur unter Platzhalternamen (nach der Hauptsitzung Handel und Bezirke); was dort steht, ist weder gelesen noch bestätigt.
- **Aufnahmen online:** keine. Ob sie mit auf die Seite sollen, hat der Spieler noch nicht gesagt; am besten nach dem nächsten Neuaufbau der Welt im Monitor, dann tragen alle denselben Lesestand und den Tag des Umzugs. Am 17.11.2026 um 20:10 Uhr lagen 15 gültige Aufnahmen vor, bis zum Spieldatum 2.6.870.
- Probeläufe des Hochlade-Skripts mit dieser Welt (Ausgabe außerhalb des Repos) liefen am 17.11.2026 ohne unbekannte Felder und ohne Fund von Privatem.
- **Angekündigt, noch nicht in den Aufnahmen:** Mit Leser 3 datiert der Monitor den Wechsel des Gönners und bei Kaufleuten den Umzug aus dem Vertrag (`spieler.lehnsherr_seit`, `spieler.lehnsherr_vertrag`, Quelle „Vertrag mit dem Gönner“). Die Welt wird beim nächsten Start des Monitors neu gelesen; danach das Faktenblatt neu erzeugen. Die beiden Felder stehen schon in den Erlaubnislisten. Kapitel I führt den 30.1.867 bis dahin als abgeleitet (Q7).

## Erzählt

### Erstes Buch: Joshua von Silberfurt (seit dem 1.1.867)

**Kapitel I · Die Reise nach Frankfurt** · Spieldatum 1.1.867 bis 2.4.867 · Stichtag Aufnahme Nr. 2, gespeichert am 17.11.2026 um 19:08 Uhr · Einschnitt vom Spieler bestätigt („Ja, so schließen“): die Ankunft in Frankfurt.

- **Bericht:** Beginn in Ulm (Gönner Welf, Zweck Händler, 50 Gold, Einkommen 0,70), Gründung am 2.1.867, Sitz Frankfurt und Gönner Liutbert, Heirat mit Cothilda (Wartenberg) am 16.2.867, Bündnis mit Nikolaus, Zweck Kunsthandwerker, am Stichtag 32,74 Gold und Einkommen 1,24. Angaben des Spielers als Q6, der Vertrag und die Familie Wartenberg als Q7.
- **Randnotiz (Abgeleitet):** Ankunft in Frankfurt am 30.1.867 aus dem Vertrag mit Liutbert; Heirat 17 Tage danach; 17,26 Gold weniger, Einkommen 0,54 höher.
- **Register:** `erster-lauf-0001` bis `-0009`; die Ankunft am 30.1.867 als `rekonstruktion`.
- **Tagebuch, neun Einträge:** Ulm am Neujahrstag; Abschrift aus dem Buch der Gesellschaft vom 2. Januar; Ulm am 9. Januar (Entschluss für Frankfurt); unterwegs am 21. Januar; Frankfurt am 30. Januar (Ankunft, Vertrag mit Liutbert); 3. Februar (Begegnung mit Cothilda an der Marktwaage); 16. Februar (Heirat); 12. März (neuer Zweck der Gesellschaft); 2. April (Rechnung zur Kasse).
- **Erzählt, also ohne Beleg im Spielstand** (für spätere Kapitel merken, damit es zusammenpasst): das Haus der Gesellschaft liegt nahe am Markt, unten Lager und Schreibstube, oben die Wohnung; die Reise mit einem gemieteten Wagen und einem Fuhrmann, Aufbruch am 11. Januar; Joshua führt neben dem Tagebuch das „Buch der Gesellschaft“ und trägt hinten im Heft ein, was an den Orten gewogen und gehandelt wird; Cothilda hat Bücher mitgebracht, liest Joshuas Einträge gegen und zählt die Kasse mit; die Begegnung an der Marktwaage mit dem Wäger und dem Jungen mit dem Korb. Die Tage der Einträge vom 9. und 21. Januar, 3. Februar und 12. März sind erzählt.
- **Bewusst offen gelassen:** warum Cothilda in Frankfurt war; ob Nikolaus bei der Heirat dabei war; was die Werkstätten fertigen und womit die Gesellschaft handelt (Handel liest der Monitor noch nicht); wofür das Gold ausgegeben wurde; ob Joshuas Eltern leben.

## Offen zu Kapitel I

- **Liutberts Titel:** In den Aufnahmen heißt er nur „Mainz“ (Schlüssel `d_et_mainz`, ein Kirchentitel ohne Stufenname). „Erzbistum“ steht deshalb nirgends im Kapitel; das Tagebuch nennt ihn „Liutbert von Mainz, den geistlichen Herrn“. Bestätigt der Spieler die Bezeichnung aus dem Spiel, kann sie in späteren Kapiteln stehen.
- **Nach dem Neuaufbau der Welt im Monitor:** Faktenblatt neu erzeugen. Trägt die Chronik des Monitors dann den 30.1.867 für Umzug und Gönner, bleibt Kapitel I, wie es ist; das Register bekommt keinen neuen Eintrag, weil der Tag dort schon als abgeleitet steht.

## Stoff für Kapitel II

Alles nach dem 2.4.867: Cothilda als Erbin (zwischen dem 2.4. und dem 14.6.867), das wachsende Prestige, die Geburt der Tochter Elisabeth am 22.6.869, die seither Erbin ist. Den Einschnitt bestätigt der Spieler; die Hauptsitzung nennt die Geburt als möglichen Schluss.

## Angaben des Spielers

Wortlaut und Lesart stehen im Dossier unter „Ergänzungen des Spielers“ und im Beiblatt `fakten/kapitel-1-beiblatt.md`.

- Warum Frankfurt? Frankfurt bringt die meisten Gewinne.
- Warum Kunsthandwerker statt Händler? Im Spiel ein Versehen des Spielers. Für die Chronik gilt der Grund, den er bestätigt hat („Ja, passt“): Joshua will für Qualität einstehen können; die Gesellschaft soll verkaufen, was ihre eigenen Werkstätten fertigen.
- Wie kam es zur Ehe mit Cothilda? Die beiden haben sich in Frankfurt kennengelernt.

## Stimmen und Formen

- **Joshua (Erstes Buch):** schreibt ruhig und genau, in der Ich-Form, meist im Perfekt. Er nennt Orte, Namen und Summen, zählt nach und liest gegen. Gefühle stehen selten da; man merkt sie an dem, was er aufschreibt. Anhalt im Dossier: Klosterschule, Freude an Handschriften, Fleiß bis in die Nacht, die Sätze von Vater und Mutter, das Vertrauen als Grundlage des Handels, der Wahlspruch.
- **Formen bisher:** Tagebucheintrag mit Datumszeile (Ort und Tag), Abschrift aus dem Buch der Gesellschaft (Urkunde), Rechnung. Noch unbenutzt: Brief, Liste, Gebet.
- **Bezugszeile:** Unter dem Etikett „Tagebuch“ steht in `hs-bezug`, zu welchen Aufnahmen erzählt wird und was Erzählung ist.
