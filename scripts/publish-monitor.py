"""Aufnahmen aus dem Paradox-Monitor auf die Seite bringen; hochgeladen wird erst nach Bestätigung.

    py -3 scripts/publish-monitor.py                    alle laufenden Läufe aus data/monitor-sources.json
    py -3 scripts/publish-monitor.py --save erster-lauf  nur ein Lauf
    py -3 scripts/publish-monitor.py --no-push          nur lokal schreiben und prüfen
    py -3 scripts/publish-monitor.py --yes              ohne Rückfrage (z. B. für geplante Aufgaben)
    py -3 scripts/publish-monitor.py --save erster-lauf --welt ck3:…          Weltkennung des Laufs festlegen
    py -3 scripts/publish-monitor.py --save erster-lauf --welt ck3:… --ausgabe ORDNER
                                                        Probelauf: Dateien nach ORDNER statt ins Repo, nichts eintragen

Der Monitor liegt neben dem Repo (`../Paradox-Monitor`, sonst `--monitor PFAD`). Gelesen wird je Welt der Ordner
`daten/ck3/<welt>/` (Aufnahmen, Chronik, Weltdaten), geschrieben wird `saves/<lauf>/data/monitor/`: `index.json`,
`verlauf.json` (Kennzahlen je Aufnahme), `chronik.json` (gültige Chronik des Monitors) und je gültiger Aufnahme
`aufnahmen/aufnahme-NNNN.json` (Spielfigur, Figuren, Titel). Verworfene Aufnahmen bleiben draußen; war eine schon
veröffentlicht, verschwindet ihre Datei wieder.

Hat ein Lauf noch keine Weltkennung, sucht das Skript die Welt über „suche“ in data/monitor-sources.json. Passt
genau eine, trägt es ihre Kennung ein; passen mehrere, nennt es sie und wartet auf `--welt`.

Nichts Privates verlässt den Monitor: Pfad und Name der Spielstand-Datei, die Steam-Kontonummer und der
Spielername stehen auf keiner Erlaubnisliste, und vor dem Schreiben wird jede Datei noch einmal darauf geprüft
(`monitor_daten.py`). Schlägt eine Prüfung an, schreibt das Skript nichts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parent
sys.path.insert(0, str(HIER))
import monitor_daten as md  # noqa: E402

QUELLEN = ROOT / "data" / "monitor-sources.json"


def einstellung_bytes(obj) -> bytes:
    """Register und Manifeste wie von Hand und von new-save.mjs: Einzug mit zwei Leerzeichen."""
    return (json.dumps(obj, ensure_ascii=False, indent=2) + chr(10)).encode("utf-8")


def spieldatum(iso) -> str:
    """„0875-02-13“ → „13.2.875“."""
    try:
        jahr, monat, tag = str(iso).split("-")
        return f"{int(tag)}.{int(monat)}.{int(jahr)}"
    except ValueError:
        return "?"


def git(*args: str, pruefen: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, check=pruefen, capture_output=True, text=True, encoding="utf-8", errors="replace")


def relativ(pfad: Path) -> str:
    return str(pfad.relative_to(ROOT)).replace("\\", "/")


def alle_geheimen_werte(monitor: Path) -> dict[str, set[str]]:
    """Kontonummern, Benutzerordner, Dateinamen und Spielernamen aus allen Welten des Monitors (alle Spiele)."""
    infos, aufnahmen = [], []
    for pfad in (monitor / "daten").glob("*/*/welt.json"):
        try:
            infos.append(json.loads(pfad.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
        aufnahmen += md.welt_lesen(pfad.parent).aufnahmen
    return md.geheime_werte(aufnahmen, [i for i in infos if isinstance(i, dict)])


def welt_des_laufs(quelle: dict, monitor: Path, gewaehlt: str | None) -> md.Welt | None:
    """Die Welt eines Laufs: festgelegt (`world_id` oder `--welt`), sonst über „suche“ gefunden."""
    kennung = gewaehlt or quelle.get("world_id")
    if kennung:
        ordner = md.welt_finden(monitor, kennung)
        if not ordner:
            print(f"{quelle['name']}: Die Welt {kennung} liegt nicht im Monitor.")
            return None
        return md.welt_lesen(ordner)
    treffer = md.welten_suchen(monitor, quelle.get("suche"))
    if not treffer:
        print(f"{quelle['name']}: noch kein Spielstand der Partie im Monitor.")
        return None
    if len(treffer) > 1:
        print(f"{quelle['name']}: Mehrere Welten passen. Bitte eine mit --save {quelle['save']} --welt KENNUNG festlegen:")
        for w in treffer:
            print(f"  {w.welt_id}  {w.info.get('name')}  ({len(w.gueltig)} Aufnahmen bis {spieldatum(w.info.get('letztes_spieldatum'))})")
        return None
    return treffer[0]


def bauen(quelle: dict, welt: md.Welt, werte: dict[str, set[str]], ziel: Path) -> tuple[dict[Path, bytes], str] | None:
    """Dateien eines Laufs (Pfad → Inhalt) und eine Zeile für die Commit-Nachricht; bricht bei Privatem ab."""
    if not welt.gueltig:
        print(f"{quelle['name']}: keine gültigen Aufnahmen für {welt.welt_id}.")
        return None
    dateien, idx = md.bauen(welt)
    funde = md.pruefen(dateien, werte)
    if funde:
        raise SystemExit("Abbruch, nichts geschrieben. Die fertigen Dateien enthalten Privates:\n  " + "\n  ".join(funde[:12]))
    neu = sorted({f for a in welt.gueltig for f in md.unbekannte_felder(a)})
    if neu:
        print(f"{quelle['name']}: Der Monitor liefert Felder, die die Chronik noch nicht kennt und deshalb nicht veröffentlicht: "
              + ", ".join(neu) + " (Erlaubnislisten in scripts/monitor_daten.py).")
    beschreibung = f"{quelle['name']} bis {spieldatum(idx['spieldatum_bis'])} ({idx['aufnahmen']} Aufnahmen)"
    return {ziel / name: inhalt for name, inhalt in dateien.items()}, beschreibung


def kennung_eintragen(quelle: dict, wid: str) -> list[Path]:
    """Weltkennung in monitor-sources.json und meta.json; das Manifest zeigt danach auf die Aufnahmen."""
    geaendert = []
    quellen = json.loads(QUELLEN.read_text(encoding="utf-8"))
    for q in quellen:
        if q.get("save") == quelle["save"] and q.get("world_id") != wid:
            q["world_id"] = wid
            QUELLEN.write_bytes(einstellung_bytes(quellen))
            geaendert.append(QUELLEN)
    daten = ROOT / "saves" / quelle["save"] / "data"
    meta_pfad, manifest_pfad = daten / "meta.json", daten / "manifest.json"
    meta = json.loads(meta_pfad.read_text(encoding="utf-8"))
    if (meta.get("monitor") or {}).get("world_id") != wid:
        meta.setdefault("monitor", {})["world_id"] = wid
        meta_pfad.write_bytes(einstellung_bytes(meta))
        geaendert.append(meta_pfad)
    manifest = json.loads(manifest_pfad.read_text(encoding="utf-8"))
    if manifest.get("monitor") != "data/monitor/index.json":
        manifest["monitor"] = "data/monitor/index.json"
        manifest_pfad.write_bytes(einstellung_bytes(manifest))
        geaendert.append(manifest_pfad)
    return geaendert


def schreiben(dateien: dict[Path, bytes], ziel: Path) -> list[Path]:
    """Nur Geändertes schreiben; Aufnahmen, die nicht mehr gültig sind, wieder entfernen."""
    geaendert = []
    for pfad, inhalt in dateien.items():
        if not pfad.exists() or pfad.read_bytes() != inhalt:
            pfad.parent.mkdir(parents=True, exist_ok=True)
            pfad.write_bytes(inhalt)
            geaendert.append(pfad)
    for alt in sorted((ziel / "aufnahmen").glob("aufnahme-*.json")):
        if alt not in dateien:
            alt.unlink()
            geaendert.append(alt)
    return geaendert


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--save", help="nur dieser Lauf (Kennung aus data/monitor-sources.json)")
    ap.add_argument("--monitor", default=str(ROOT.parent / "Paradox-Monitor"), help="Ordner des Paradox-Monitors")
    ap.add_argument("--welt", help="Weltkennung (ck3:…) für den Lauf aus --save festlegen")
    ap.add_argument("--ausgabe", help="Probelauf: Dateien in diesen Ordner statt ins Repo schreiben, nichts eintragen")
    ap.add_argument("--no-push", action="store_true", help="nur lokal schreiben und prüfen")
    ap.add_argument("--yes", action="store_true", help="ohne Rückfrage hochladen")
    args = ap.parse_args(argv)
    for strom in (sys.stdout, sys.stderr):          # Namen aus dem Spiel dürfen keine Ausgabe zum Absturz bringen
        if hasattr(strom, "reconfigure"):
            strom.reconfigure(errors="replace")

    monitor = Path(args.monitor)
    if not (monitor / "daten").is_dir():
        print(f"Paradox-Monitor nicht gefunden: {monitor}", file=sys.stderr)
        return 2
    if args.welt and not args.save:
        print("--welt braucht --save: Zu welchem Lauf gehört die Welt?", file=sys.stderr)
        return 2
    alle = json.loads(QUELLEN.read_text(encoding="utf-8"))
    if args.save:
        quellen = [q for q in alle if q["save"] == args.save]
        if not quellen:
            print(f"Lauf „{args.save}“ steht nicht in data/monitor-sources.json.", file=sys.stderr)
            return 2
    else:
        # Abgeschlossene Läufe („abgeschlossen“ in monitor-sources.json) lädt nur noch ein ausdrückliches --save hoch.
        quellen = [q for q in alle if not q.get("abgeschlossen")]
        for q in alle:
            if q.get("abgeschlossen"):
                print(f"{q['name']}: abgeschlossen am {q['abgeschlossen'].get('datum')}, wird übersprungen.")
        if not quellen:
            print("Kein laufender Lauf in data/monitor-sources.json.")
            return 0

    probe = Path(args.ausgabe) if args.ausgabe else None
    hochladen = not args.no_push and not probe
    hat_commit = git("rev-parse", "--verify", "-q", "HEAD", pruefen=False).returncode == 0
    if hochladen and git("remote", pruefen=False).stdout.strip():
        git("fetch", "origin", pruefen=False)
        if hat_commit and git("rev-parse", "--verify", "-q", "origin/main", pruefen=False).returncode == 0:
            r = git("merge", "--ff-only", "origin/main", pruefen=False)
            if r.returncode != 0:
                print("GitHub-Stand lässt sich nur mit Zusammenführen übernehmen; bitte zuerst von Hand klären.\n" + r.stderr,
                      file=sys.stderr)
                return 3

    werte = alle_geheimen_werte(monitor)
    pfade: list[Path] = []
    beschreibungen: list[str] = []
    for quelle in quellen:
        welt = welt_des_laufs(quelle, monitor, args.welt)
        if not welt:
            continue
        ziel = (probe / quelle["save"] if probe else ROOT / "saves" / quelle["save"]) / "data" / "monitor"
        ergebnis = bauen(quelle, welt, werte, ziel)
        if not ergebnis:
            continue
        dateien, beschreibung = ergebnis
        if not probe:
            if quelle.get("world_id") != welt.welt_id:
                print(f"{quelle['name']}: Welt „{welt.info.get('name')}“ ({welt.welt_id}) eingetragen.")
            pfade += kennung_eintragen(quelle, welt.welt_id)
        pfade += schreiben(dateien, ziel)
        beschreibungen.append(beschreibung)

    if probe:
        print(f"Probelauf: {len(pfade)} Dateien unter {probe} geschrieben, im Repo nichts geändert. " + "; ".join(beschreibungen))
        return 0
    if not pfade:
        print("Keine neuen Aufnahmen.")
        return 0
    pruefung = subprocess.run(["node", "scripts/validate-data.mjs"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(pruefung.stdout.strip())
    if pruefung.returncode != 0:
        print("Prüfung fehlgeschlagen, nichts committet.\n" + pruefung.stderr, file=sys.stderr)
        return 4
    namen = sorted({relativ(p) for p in pfade})
    print("Geändert:\n  " + "\n  ".join(namen))
    treffer = md.repo_funde(ROOT, werte)
    if treffer:
        print("Im Repo steht Privates aus dem Monitor, nichts committet:", *treffer, sep=chr(10) + "  ", file=sys.stderr)
        return 4
    if not hochladen:
        return 0
    if not hat_commit:
        print("Das Repo hat noch keinen ersten Commit. Die Dateien bleiben lokal; hochgeladen wird mit dem Gerüst.")
        return 0
    if not args.yes and input("Hochladen? [j/N] ").strip().lower() not in ("j", "ja", "y", "yes"):
        print("Nicht hochgeladen; die Dateien bleiben lokal.")
        return 0
    # Den Ordner der Aufnahmen als Ganzes vormerken: So gehen auch entfernte (verworfene) Aufnahmen in den Commit.
    vormerken = sorted({n.split("/data/monitor/")[0] + "/data/monitor" if "/data/monitor/" in n else n for n in namen})
    git("add", "-A", "--", *vormerken)
    git("commit", "-m", "Aufnahmen " + "; ".join(beschreibungen))
    r = git("push", "origin", "HEAD:main", pruefen=False)
    if r.returncode != 0:
        print("Push fehlgeschlagen:\n" + r.stderr, file=sys.stderr)
        return 5
    print("Hochgeladen: " + "; ".join(beschreibungen))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
