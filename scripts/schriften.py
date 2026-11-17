"""Schriften der CK3-Chronik aus den Originalen bauen: auf lateinische Zeichen verkleinern, als WOFF2 speichern.

Aufruf (lokal, braucht fontTools und brotli; die Originale liegen nicht im Repo):

    py -3 scripts/schriften.py ORDNER_MIT_ORIGINALEN          WOFF2 nach assets/fonts/ schreiben, Tabelle ausgeben
    py -3 scripts/schriften.py --pruefen                      nur die Dateien in assets/fonts/ prüfen

ORDNER_MIT_ORIGINALEN enthält die Dateien aus github.com/google/fonts (Ordner ofl/texturina und ofl/ebgaramond),
so wie `assets/fonts/QUELLEN.md` sie nennt. Beide Schriften stehen unter der SIL Open Font License 1.1 und
haben keinen „Reserved Font Name“; Verkleinern, Umwandeln und Ergänzen ist damit erlaubt, solange Urhebervermerk
und Lizenz mitgehen. Das Skript bricht ab, wenn eine Datei die OFL nicht in ihren Namenseinträgen trägt.

Geändert wird dreierlei: der Zeichenvorrat (ZEICHEN), das Format (WOFF2, ohne Hinting) und bei EB Garamond die
Kapitälchen der deutschen Sprachformen (siehe kapitaelchen_ergaenzen).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZIEL = ROOT / "assets" / "fonts"

# Lateinische Schrift für Namen aus allen Kulturen des Spiels (gezählt am deutschen Spieltext von CK3 1.21):
# Latin-1, Latin Extended-A und -B, einzelne Lautzeichen, Modifikatoren (ʿ ʻ), kombinierende Akzente,
# Latin Extended Additional (Punkte unter Konsonanten, Vietnamesisch), Satzzeichen, Hoch- und Tiefstellung,
# Währung, Zahlzeichen, Pfeile, Minus und Vergleiche, Schlussblätter.
ZEICHEN = ("U+0020-007E,U+00A0-00FF,U+0100-017F,U+0180-024F,U+0259,U+02B0-02FF,U+0300-036F,U+1E00-1EFF,"
           "U+2000-206F,U+2070-209F,U+20A0-20BF,U+2116,U+2150-218F,U+2190-2193,U+2212,U+2260-2265,"
           "U+2619,U+2766-2767")

TEXT_MERKMALE = "kern,mark,mkmk,ccmp,locl,liga,calt,rlig,onum,lnum,pnum,tnum,smcp,c2sc,case,frac,sups,ordn"
TITEL_MERKMALE = "kern,mark,mkmk,ccmp,locl,liga,onum,lnum,case"

# Ziel, Original (relativ zum Ordner der Originale), OpenType-Merkmale
SCHRIFTEN = (
    ("texturina.woff2", "texturina/Texturina[opsz,wght].ttf", TITEL_MERKMALE),
    ("eb-garamond.woff2", "ebgaramond/EBGaramond[wght].ttf", TEXT_MERKMALE),
    ("eb-garamond-italic.woff2", "ebgaramond/EBGaramond-Italic[wght].ttf", TEXT_MERKMALE),
)
LIZENZTEXTE = (("OFL-Texturina.txt", "texturina/OFL.txt"), ("OFL-EBGaramond.txt", "ebgaramond/OFL.txt"))


def sha256(pfad: Path) -> str:
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def namen(pfad: Path) -> dict:
    """Namenseinträge einer Schriftdatei: Familie, Version, Urheber, Lizenz, dazu Achsen und Zeichenzahl."""
    from fontTools.ttLib import TTFont

    schrift = TTFont(pfad)
    tabelle = schrift["name"]
    eintrag = lambda nr: tabelle.getDebugName(nr) or ""
    achsen = [(a.axisTag, int(a.minValue), int(a.maxValue)) for a in schrift["fvar"].axes] if "fvar" in schrift else []
    return {"familie": eintrag(1), "version": eintrag(5), "urheber": eintrag(0), "lizenz": eintrag(13),
            "lizenz_url": eintrag(14), "achsen": achsen, "zeichen": len(schrift.getBestCmap())}


def ofl_pruefen(pfad: Path, info: dict) -> None:
    if "SIL Open Font License, Version 1.1" not in info["lizenz"] or not info["urheber"].startswith("Copyright"):
        raise SystemExit(f"{pfad.name}: Die Namenseinträge nennen die SIL Open Font License 1.1 nicht. Nicht verwenden.")


def kapitaelchen_ergaenzen(schrift) -> list[str]:
    """Deutsche Sprachformen bekommen ihr Kapitälchen.

    EB Garamond ersetzt in deutschem Text f, Ä, Ö und Ü durch eigene Formen (Merkmal locl, Sprache DEU), kennt für
    diese Formen aber kein Kapitälchen: In einer Kapitälchenzeile bliebe das f klein und der Umlaut groß. Hier
    bekommt jede dieser Formen das Kapitälchen ihres Grundzeichens."""
    gsub = schrift["GSUB"].table

    def tabellen(indizes):
        for i in indizes:
            for teil in gsub.LookupList.Lookup[i].SubTable:
                teil = getattr(teil, "ExtSubTable", teil)
                if isinstance(getattr(teil, "mapping", None), dict):
                    yield teil.mapping

    formen: dict[str, str] = {}
    for schriftsystem in gsub.ScriptList.ScriptRecord:
        for sprache in schriftsystem.Script.LangSysRecord:
            if schriftsystem.ScriptTag != "latn" or sprache.LangSysTag.strip() != "DEU":
                continue
            for nr in sprache.LangSys.FeatureIndex:
                merkmal = gsub.FeatureList.FeatureRecord[nr]
                if merkmal.FeatureTag == "locl":
                    for zuordnung in tabellen(merkmal.Feature.LookupListIndex):
                        formen.update(zuordnung)
    ergaenzt = []
    for merkmal in gsub.FeatureList.FeatureRecord:
        if merkmal.FeatureTag in ("smcp", "c2sc"):
            for zuordnung in tabellen(merkmal.Feature.LookupListIndex):
                for grund, form in formen.items():
                    if grund in zuordnung and form not in zuordnung:
                        zuordnung[form] = zuordnung[grund]
                        ergaenzt.append(f"{merkmal.FeatureTag}: {form} → {zuordnung[grund]}")
    return sorted(set(ergaenzt))


def bauen(quelle: Path) -> None:
    import tempfile

    from fontTools import subset
    from fontTools.ttLib import TTFont

    ZIEL.mkdir(parents=True, exist_ok=True)
    for ziel, original, _ in SCHRIFTEN:
        ofl_pruefen(quelle / original, namen(quelle / original))
    for ziel, original in LIZENZTEXTE:
        text = (quelle / original).read_text(encoding="utf-8")
        kopf = text.split("This Font Software is licensed", 1)[0]
        if "SIL OPEN FONT LICENSE Version 1.1" not in text or "Reserved Font Name" in kopf:
            raise SystemExit(f"{original}: kein OFL-1.1-Text oder mit „Reserved Font Name“ im Urhebervermerk.")
        (ZIEL / ziel).write_bytes((quelle / original).read_bytes())
    with tempfile.TemporaryDirectory() as zwischen:
        for ziel, original, merkmale in SCHRIFTEN:
            schrift = TTFont(quelle / original, recalcTimestamp=False)
            for zeile in kapitaelchen_ergaenzen(schrift):
                print(f"{ziel}: Kapitälchen ergänzt, {zeile}")
            vorlage = Path(zwischen) / ziel.replace(".woff2", ".ttf")
            schrift.save(vorlage)
            subset.main([str(vorlage), f"--output-file={ZIEL / ziel}", "--flavor=woff2", f"--unicodes={ZEICHEN}",
                         f"--layout-features={merkmale}", "--name-IDs=*", "--name-languages=*", "--notdef-outline",
                         "--no-hinting", "--desubroutinize", "--no-recalc-timestamp"])


def tabelle(quelle: Path | None) -> int:
    fehler = 0
    for ziel, original, _ in SCHRIFTEN:
        pfad = ZIEL / ziel
        if not pfad.exists():
            print(f"{ziel}: fehlt")
            fehler += 1
            continue
        info = namen(pfad)
        ofl_pruefen(pfad, info)
        achsen = ", ".join(f"{tag} {von}–{bis}" for tag, von, bis in info["achsen"]) or "keine"
        print(f"{ziel}: {info['familie']}, {info['version']}, {info['zeichen']} Zeichen, Achsen {achsen}, {pfad.stat().st_size} Bytes")
        print(f"  Urheber: {info['urheber']}")
        print(f"  Lizenz laut Datei: {info['lizenz']}")
        print(f"  SHA-256: {sha256(pfad)}")
        if quelle:
            print(f"  Original {original}: SHA-256 {sha256(quelle / original)}")
    for ziel, _ in LIZENZTEXTE:
        pfad = ZIEL / ziel
        print(f"{ziel}: {'SHA-256 ' + sha256(pfad) if pfad.exists() else 'fehlt'}")
        fehler += 0 if pfad.exists() else 1
    return 1 if fehler else 0


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    if argv[0] == "--pruefen":
        return tabelle(None)
    quelle = Path(argv[0])
    bauen(quelle)
    return tabelle(quelle)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
