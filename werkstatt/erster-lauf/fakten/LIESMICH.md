# Faktenblätter

Je Kapitel ein Faktenblatt `kapitel-N.md` aus den Aufnahmen des Paradox-Monitors für den Zeitraum des Kapitels. Erzeugt von `scripts/fakten.py`, nicht von Hand ändern.

```text
py -3 scripts/fakten.py --save erster-lauf --kapitel 1 --bis 0867-04-02
py -3 scripts/fakten.py --save erster-lauf --kapitel 2 --von 0867-04-02 --bis JJJJ-MM-TT
```

`--bis` ist der Stichtag des Kapitels (Spieldatum der letzten verwendeten Aufnahme), `--von` der Stichtag des Kapitels davor. Nach einem Neuaufbau der Welt im Monitor erzeugt man die Blätter neu; ein unverändertes Blatt bleibt Byte für Byte gleich.

Im Kopf steht der Lesestand der Spielversion: der jüngste Vermerk des Monitors, mit der Aufnahme, seit der er gilt. Die Tabelle darunter zeigt je Aufnahme den Vermerk beim Lesen.

## Beiblatt

Was die Aufnahmen für ein Kapitel nicht hergeben, steht im Beiblatt `kapitel-N-beiblatt.md`: die Angaben des Spielers zu Gründen und Entscheidungen, Funde aus dem Spielstand, die der Monitor noch nicht aufnimmt, und Texte des Spiels. Das Beiblatt führt eine Sitzung von Hand. `scripts/fakten.py` hängt es an das Faktenblatt an und prüft es mit auf Privates; im Kopf des Faktenblatts steht dann ein Verweis darauf. Wer das Beiblatt ändert, erzeugt das Faktenblatt neu.
