"""Ornamente der CK3-Chronik erzeugen: Randleisten, Titelrahmen, Vierpass und Initialgrund als SVG, Pergament als PNG.

Aufruf: py -3 scripts/ornamente.py            schreibt die Dateien nach assets/
        py -3 scripts/ornamente.py --pruefen  vergleicht nur (Rückgabe 1, wenn eine Datei abweicht)

Alles hier ist eigene Zeichnung aus Formeln, ohne fremde Pakete; Spielgrafik kommt nicht vor. Drei Arten von Dateien:

- Masken (einfarbig schwarz): Das Stylesheet färbt sie über `mask-image` mit den Farben der Chronik ein.
  `ranke.svg` und `ranke-knospen.svg` bilden zusammen die Blattranke (Stiel und Blätter getrennt, damit
  sie zwei Farben tragen können), dazu die senkrechten Fassungen und der `vierpass.svg`.
- Bilder mit festen Farben, je eine Fassung für hell und dunkel: der Titelrahmen (`rahmen-*.svg`, für
  `border-image`) und das Pergament (`pergament-*.png`, eine Kachel aus berechneten Wolken). Die Farben stehen
  unten in FARBEN und PERGAMENT und müssen zu den Variablen in `assets/handschrift.css` passen.
- `initiale-grund.svg` (Rautengrund hinter den Schmuckinitialen) und `zeichen.svg` (Zeichen im Browser-Tab).
"""

from __future__ import annotations

import math
import struct
import sys
import zlib
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Wie in assets/handschrift.css (--hs-gold, --hs-rubrum, --hs-blau), je für hell und dunkel
FARBEN = {
    "hell": {"gold": "#a8842c", "rot": "#9c1f17", "blau": "#23407a"},
    "dunkel": {"gold": "#cba95a", "rot": "#ee9079", "blau": "#a3bdf0"},
}
# Pergament: Farbe der Wolken und ihre größte Deckkraft. Die dunkelste (hell) und die hellste (dunkel) Stelle,
# die daraus entstehen kann, steht im Stylesheet als --hs-papier-fleck; scripts/kontrast.mjs rechnet sie aus der
# Kachel nach und prüft die Schrift auch gegen sie.
PERGAMENT = {
    "hell": {"farbe": (92, 61, 26), "wolken": 0.10},
    "dunkel": {"farbe": (242, 227, 191), "wolken": 0.06},
}

BREITE, HOEHE, MITTE, HUB = 48.0, 16.0, 8.0, 3.2   # eine Welle der Ranke


def z(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def stiel_y(x: float) -> float:
    return MITTE - HUB * math.sin(2 * math.pi * x / BREITE)


def _gleiten(punkte: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Dasselbe Motiv eine halbe Welle weiter und gespiegelt (Gleitspiegelung der Ranke)."""
    return [(x + BREITE / 2, HOEHE - y) for x, y in punkte]


def _blatt(fuss: tuple[float, float], spitze: tuple[float, float], breite: float) -> list[tuple[float, float]]:
    """Blatt als zwei Bögen vom Fuß zur Spitze: Fuß, Stützpunkt, Spitze, Stützpunkt."""
    (bx, by), (tx, ty) = fuss, spitze
    laenge = math.hypot(tx - bx, ty - by)
    dx, dy = (tx - bx) / laenge, (ty - by) / laenge
    mx, my = bx + dx * laenge * 0.42, by + dy * laenge * 0.42
    return [fuss, (mx - dy * breite, my + dx * breite), spitze, (mx + dy * breite, my - dx * breite)]


def ranke_teile() -> dict:
    """Stiel, Blätter und Beeren einer Welle (48 × 16), über die Ränder hinaus gezeichnet, damit die Kachel schließt."""
    stiel = [(x / 2, stiel_y(x / 2)) for x in range(-4, int(BREITE * 2) + 5)]
    blatt_oben = _blatt((7.0, stiel_y(7.0)), (15.4, 11.9), 2.7)          # in der Bucht unter dem Wellenberg
    beere_oben, stengel_oben = (12.0, 1.75), [(12.0, stiel_y(12.0)), (12.0, 2.8)]
    blaetter, beeren, stengel = [], [], []
    for versatz in (-BREITE, 0.0, BREITE):
        schieben = lambda punkte: [(x + versatz, y) for x, y in punkte]
        blaetter += [schieben(blatt_oben), schieben(_gleiten(blatt_oben))]
        beeren += schieben([beere_oben]) + schieben(_gleiten([beere_oben]))
        stengel += [schieben(stengel_oben), schieben(_gleiten(stengel_oben))]
    return {"stiel": stiel, "blaetter": blaetter, "beeren": beeren, "stengel": stengel}


def _zug(punkte, wechsel=lambda p: p) -> str:
    return "M" + " L".join(f"{z(x)} {z(y)}" for x, y in map(wechsel, punkte))


def _blattpfad(b, wechsel=lambda p: p) -> str:
    (fx, fy), (ax, ay), (sx, sy), (cx, cy) = map(wechsel, b)
    return f"M{z(fx)} {z(fy)} Q{z(ax)} {z(ay)} {z(sx)} {z(sy)} Q{z(cx)} {z(cy)} {z(fx)} {z(fy)}Z"


def _svg(breite: float, hoehe: float, inhalt: str, masse: tuple[float, float] | None = None) -> str:
    w, h = masse or (breite, hoehe)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{z(w)}" height="{z(h)}" '
            f'viewBox="0 0 {z(breite)} {z(hoehe)}">{inhalt}</svg>\n')


def ranke(senkrecht: bool = False) -> str:
    """Stiel der Ranke mit den Stengeln der Beeren (Maske)."""
    t = ranke_teile()
    wechsel = (lambda p: (p[1], p[0])) if senkrecht else (lambda p: p)
    wege = [_zug(t["stiel"], wechsel)] + [_zug(s, wechsel) for s in t["stengel"]]
    inhalt = (f'<path d="{" ".join(wege)}" fill="none" stroke="#000" stroke-width="1.4" '
              'stroke-linecap="round" stroke-linejoin="round"/>')
    return _svg(HOEHE, BREITE, inhalt) if senkrecht else _svg(BREITE, HOEHE, inhalt)


def ranke_knospen(senkrecht: bool = False) -> str:
    """Blätter und Beeren der Ranke (Maske), deckungsgleich mit ranke()."""
    t = ranke_teile()
    wechsel = (lambda p: (p[1], p[0])) if senkrecht else (lambda p: p)
    blaetter = " ".join(_blattpfad(b, wechsel) for b in t["blaetter"])
    beeren = "".join(f'<circle cx="{z(wechsel(b)[0])}" cy="{z(wechsel(b)[1])}" r="1.25"/>' for b in t["beeren"])
    inhalt = f'<path d="{blaetter}"/>{beeren}'
    return _svg(HOEHE, BREITE, inhalt) if senkrecht else _svg(BREITE, HOEHE, inhalt)


def _pass(mitte: float, abstand: float, radius: float) -> str:
    """Umriss eines Vierpasses: vier Kreisbögen um die Mitte, jeder von Schnittpunkt zu Schnittpunkt."""
    t = (math.sqrt(2) * abstand + math.sqrt(4 * radius ** 2 - 2 * abstand ** 2)) / 2   # Schnittpunkt auf der Diagonale
    s = t / math.sqrt(2)
    ecken = [(mitte - s, mitte - s), (mitte + s, mitte - s), (mitte + s, mitte + s), (mitte - s, mitte + s)]
    weg = f"M{z(ecken[0][0])} {z(ecken[0][1])}"
    for x, y in ecken[1:] + ecken[:1]:
        weg += f" A{z(radius)} {z(radius)} 0 1 1 {z(x)} {z(y)}"
    return weg + "Z"


def vierpass() -> str:
    """Vierpass mit Innenlinie, Mittelstern und vier Punkten (Maske, 100 × 100)."""
    aussen, innen = _pass(50, 21, 21), _pass(50, 21, 16)
    stern = "M50 38.5 L52.9 47.1 L61.5 50 L52.9 52.9 L50 61.5 L47.1 52.9 L38.5 50 L47.1 47.1Z"
    punkte = "".join(f'<circle cx="{z(50 + 21 * dx)}" cy="{z(50 + 21 * dy)}" r="3.4"/>'
                     for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)))
    inhalt = (f'<g fill="none" stroke="#000" stroke-linejoin="round"><path d="{aussen}" stroke-width="3.2"/>'
              f'<path d="{innen}" stroke-width="1.5"/></g><path d="{stern}"/>{punkte}')
    return _svg(100, 100, inhalt)


def rahmen(modus: str) -> str:
    """Titelrahmen für `border-image` (96 × 96, Schnitt bei 24): Ranke an den Seiten, Rosetten in den Ecken."""
    f = FARBEN[modus]
    t = ranke_teile()
    heben = lambda p: (p[0] + 24, p[1] + 4)                    # Leiste oben: 48 breit, 24 hoch, Ranke in der Mitte
    innerhalb = lambda punkte: all(-6 <= x <= BREITE + 6 for x, _ in punkte)
    stiel = [p for p in t["stiel"] if 0 <= p[0] <= BREITE]
    wege = [_zug(stiel, heben)] + [_zug(s, heben) for s in t["stengel"] if innerhalb(s)]
    blaetter = " ".join(_blattpfad(b, heben) for b in t["blaetter"] if innerhalb(b))
    beeren = "".join(f'<circle cx="{z(x + 24)}" cy="{z(y + 4)}" r="1.25"/>' for x, y in t["beeren"] if 0 <= x <= BREITE)
    seite = (
        f'<clipPath id="leiste"><rect x="24" y="0" width="48" height="24"/></clipPath>'
        f'<g clip-path="url(#leiste)"><path d="{" ".join(wege)}" fill="none" stroke="{f["gold"]}" stroke-width="1.4" '
        f'stroke-linecap="round" stroke-linejoin="round"/><path d="{blaetter}" fill="{f["rot"]}"/>'
        f'<g fill="{f["blau"]}">{beeren}</g></g>'
        f'<path d="M24 1.25 H72 M24 22.9 H72" fill="none" stroke="{f["gold"]}" stroke-width="0.9"/>'
    )
    blaettchen = "".join(f'<circle cx="{z(12 + 3.3 * dx)}" cy="{z(12 + 3.3 * dy)}" r="2.35"/>'
                         for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)))
    ecke = (
        f'<path d="M1.25 24 V1.25 H24 M22.9 24 V22.9 H24 M24 12 H19 M12 24 V19" fill="none" stroke="{f["gold"]}" stroke-width="0.9"/>'
        f'<circle cx="12" cy="12" r="7" fill="none" stroke="{f["gold"]}" stroke-width="1.1"/>'
        f'<g fill="{f["rot"]}">{blaettchen}</g><circle cx="12" cy="12" r="1.5" fill="{f["blau"]}"/>'
    )
    viertel = "".join(f'<g transform="rotate({90 * k} 48 48)">{ecke}{seite.replace("leiste", f"leiste{k}")}</g>' for k in range(4))
    return _svg(96, 96, viertel)


def initiale_grund() -> str:
    """Rautengrund hinter den Schmuckinitialen (Kachel 12 × 12, goldene Linien und Punkte, halb durchscheinend)."""
    inhalt = ('<g fill="none" stroke="#b08d3c" stroke-width="0.7" opacity="0.55"><path d="M0 6 L6 0 L12 6 L6 12Z"/></g>'
              '<g fill="#b08d3c" opacity="0.6"><circle cx="6" cy="6" r="0.9"/><circle cx="0" cy="0" r="0.9"/>'
              '<circle cx="12" cy="0" r="0.9"/><circle cx="0" cy="12" r="0.9"/><circle cx="12" cy="12" r="0.9"/></g>')
    return _svg(12, 12, inhalt)


def _zufall(saat: int, i: int, j: int) -> float:
    """Fester Zufallswert 0..1 für einen Gitterpunkt (ganzzahlige Streuung, auf jedem Rechner gleich)."""
    h = (i * 374761393 + j * 668265263 + saat * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFF) / 0xFFFFFF


def _wolken(n: int, saat: int) -> list[list[float]]:
    """Weiches, kachelbares Rauschen (n × n, Werte 0..1): vier Lagen, jede doppelt so fein wie die vorige.

    Die gröbste Lage wiegt wenig, damit sich die Kachel beim Aneinanderlegen nicht als Muster verrät."""
    feld = [[0.0] * n for _ in range(n)]
    gesamt = 0.0
    for lage, (zellen, gewicht) in enumerate(((4, 0.45), (8, 1.0), (16, 0.7), (32, 0.4))):
        gesamt += gewicht
        gitter = [[_zufall(saat + lage, i, j) for i in range(zellen)] for j in range(zellen)]
        schritt = zellen / n
        weich = [(lambda t: t * t * (3 - 2 * t))((x * schritt) % 1.0) for x in range(n)]
        zelle = [int(x * schritt) % zellen for x in range(n)]
        for y in range(n):
            j0, ty = zelle[y], weich[y]
            oben, unten = gitter[j0], gitter[(j0 + 1) % zellen]
            zeile = feld[y]
            for x in range(n):
                i0, tx = zelle[x], weich[x]
                i1 = (i0 + 1) % zellen
                a = oben[i0] + (oben[i1] - oben[i0]) * tx
                b = unten[i0] + (unten[i1] - unten[i0]) * tx
                zeile[x] += (a + (b - a) * ty) * gewicht
    return [[v / gesamt for v in zeile] for zeile in feld]


def _png(breite: int, hoehe: int, palette: list[tuple[int, int, int, int]], zeilen: list[bytes]) -> bytes:
    """PNG mit Farbtabelle und Deckkraft je Eintrag, ohne fremde Pakete."""
    def block(art: bytes, daten: bytes) -> bytes:
        return struct.pack(">I", len(daten)) + art + daten + struct.pack(">I", zlib.crc32(art + daten) & 0xFFFFFFFF)

    roh = b"".join(b"\x00" + zeile for zeile in zeilen)
    return (b"\x89PNG\r\n\x1a\n" + block(b"IHDR", struct.pack(">IIBBBBB", breite, hoehe, 8, 3, 0, 0, 0))
            + block(b"PLTE", b"".join(bytes(p[:3]) for p in palette)) + block(b"tRNS", bytes(p[3] for p in palette))
            + block(b"IDAT", zlib.compress(roh, 9)) + block(b"IEND", b""))


def _png_inhalt(daten: bytes) -> tuple:
    """Kopf, Farbtabelle, Deckkraft und entpackte Bildzeilen eines PNG (zum Vergleich unabhängig von der Packstufe)."""
    teile, ort = {}, 8
    while ort < len(daten):
        laenge, art = struct.unpack(">I4s", daten[ort:ort + 8])
        teile[art] = teile.get(art, b"") + daten[ort + 8:ort + 8 + laenge]
        ort += 12 + laenge
    return teile.get(b"IHDR"), teile.get(b"PLTE"), teile.get(b"tRNS"), zlib.decompress(teile.get(b"IDAT", b""))


def pergament(modus: str) -> bytes:
    """Wolkiges Pergament als Kachel (256 × 256, PNG; das Stylesheet zeigt sie doppelt so groß): weiche Wolken
    als Schleier über der Papierfarbe.

    Die Farbe ist überall dieselbe, nur die Deckkraft wechselt; deshalb genügt eine kleine Farbtabelle."""
    p = PERGAMENT[modus]
    n = 256
    stuetzen = (0.0, 0.0, 0.08, 0.25, 0.5, 0.75, 0.92, 1.0, 1.0)   # sanfter Anstieg, Deckel oben

    def kurve(v: float) -> float:
        t = min(max(v, 0.0), 1.0) * (len(stuetzen) - 1)
        i = min(int(t), len(stuetzen) - 2)
        return stuetzen[i] + (stuetzen[i + 1] - stuetzen[i]) * (t - i)

    wolken = _wolken(n, 11 if modus == "hell" else 23)
    tief = min(min(zeile) for zeile in wolken)
    hoch = max(max(zeile) for zeile in wolken)
    zeilen = [bytes(round(p["wolken"] * kurve((v - tief) / (hoch - tief)) * 255) for v in zeile) for zeile in wolken]
    hoechste = max(max(zeile) for zeile in zeilen)
    return _png(n, n, [(*p["farbe"], deckkraft) for deckkraft in range(hoechste + 1)], zeilen)


def zeichen() -> str:
    """Zeichen für den Browser-Tab: roter Vierpass auf Pergament."""
    f = FARBEN["hell"]
    inhalt = (f'<rect width="100" height="100" rx="14" fill="#efe3c6"/>'
              f'<path d="{_pass(50, 23, 21)}" fill="none" stroke="{f["rot"]}" stroke-width="6" stroke-linejoin="round"/>'
              f'<circle cx="50" cy="50" r="9" fill="{f["blau"]}"/>')
    return _svg(100, 100, inhalt, masse=(64, 64))


def dateien() -> dict[str, str | bytes]:
    return {
        "ranke.svg": ranke(), "ranke-knospen.svg": ranke_knospen(),
        "ranke-senkrecht.svg": ranke(senkrecht=True), "ranke-knospen-senkrecht.svg": ranke_knospen(senkrecht=True),
        "vierpass.svg": vierpass(), "rahmen-hell.svg": rahmen("hell"), "rahmen-dunkel.svg": rahmen("dunkel"),
        "initiale-grund.svg": initiale_grund(), "pergament-hell.png": pergament("hell"),
        "pergament-dunkel.png": pergament("dunkel"), "zeichen.svg": zeichen(),
    }


def gleich(pfad: Path, inhalt: str | bytes) -> bool:
    if not pfad.exists():
        return False
    if isinstance(inhalt, bytes):                                    # PNG: Bildinhalt vergleichen, nicht die Packung
        return _png_inhalt(pfad.read_bytes()) == _png_inhalt(inhalt)
    return pfad.read_text(encoding="utf-8") == inhalt


def main(argv: list[str]) -> int:
    pruefen = "--pruefen" in argv
    abweichend = []
    for name, inhalt in dateien().items():
        pfad = ASSETS / name
        if pruefen:
            if not gleich(pfad, inhalt):
                abweichend.append(name)
        elif isinstance(inhalt, bytes):
            pfad.write_bytes(inhalt)
        else:
            pfad.write_text(inhalt, encoding="utf-8", newline="\n")
    if pruefen:
        print("Ornamente weichen vom Skript ab: " + ", ".join(abweichend) if abweichend else "Ornamente entsprechen dem Skript.")
        return 1 if abweichend else 0
    print(", ".join(dateien()), "geschrieben")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
