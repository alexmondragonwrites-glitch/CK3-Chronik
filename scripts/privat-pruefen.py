"""Das Repo nach den privaten Werten aus dem Paradox-Monitor durchsuchen (lokal, vor jedem Hochladen von Hand).

    py -3 scripts/privat-pruefen.py [--monitor PFAD]

`validate-data.mjs` erkennt Privates an Mustern (Pfade, Steam-Ordner, Dateinamen von Spielständen). Dieses Skript
kennt dazu die Werte selbst: Es liest Kontonummer, Benutzerordner, Dateinamen und Spielernamen aus den Daten des
Monitors und sucht sie in jeder Datei des Repos, auch in Kapiteln, Doku und Bildern. Die Werte bleiben im
Speicher; ausgegeben werden nur Datei und Art des Fundes. Ohne Monitor (etwa in der GitHub-Prüfung) gibt es
nichts zu vergleichen, das Skript meldet das und endet ohne Fehler.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parent
sys.path.insert(0, str(HIER))
import monitor_daten as md  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--monitor", default=str(ROOT.parent / "Paradox-Monitor"), help="Ordner des Paradox-Monitors")
    args = ap.parse_args(argv)
    monitor = Path(args.monitor)
    if not (monitor / "daten").is_dir():
        print(f"Kein Paradox-Monitor unter {monitor}: nichts zu vergleichen.")
        return 0
    spec = importlib.util.spec_from_file_location("publish_monitor", HIER / "publish-monitor.py")
    publish = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(publish)
    werte = publish.alle_geheimen_werte(monitor)
    anzahl = ", ".join(f"{len(menge)} × {art}" for art, menge in werte.items())
    funde = md.repo_funde(ROOT, werte)
    if funde:
        print(f"Privates aus dem Monitor im Repo ({anzahl} bekannt):", file=sys.stderr)
        for f in funde:
            print("  - " + f, file=sys.stderr)
        return 1
    print(f"Kein privater Wert aus dem Monitor im Repo ({anzahl} bekannt).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
