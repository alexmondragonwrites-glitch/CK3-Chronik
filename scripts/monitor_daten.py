"""Aufnahmen des Paradox-Monitors für die öffentliche Seite auswählen und von Privatem befreien.

Der Monitor legt je Welt (Partie) einen Ordner `daten/ck3/<welt>/` an: `daten.jsonl` (eine Aufnahme je Zeile,
bei ruhenden Welten als `daten.jsonl.xz`), `chronik.jsonl` und `welt.json`. Dieses Modul liest so einen Ordner
und baut daraus die Dateien für `saves/<lauf>/data/monitor/`. Es braucht dafür weder den Code des Monitors noch
Git und läuft deshalb auch in der GitHub-Prüfung; `publish-monitor.py` schreibt die Dateien und lädt hoch.

Drei Sicherungen halten Privates draußen:

1. Erlaubnislisten: Veröffentlicht wird nur, was hier als Feld genannt ist. Der Block `datei` (Pfad mit der
   Steam-Kontonummer, Dateiname, Prüfsumme), `kampagne.spielername` und in `welt.json` das Feld `letzte_datei`
   stehen auf keiner Liste. Neue Felder des Monitors bleiben draußen, bis jemand sie hier einträgt.
2. Muster (`privat_funde`): Pfade, Steam-Ordner, Dateinamen von Spielständen, Kontokennungen und die Schlüssel
   der privaten Felder schlagen an, wo immer sie in den fertigen Dateien stehen.
3. Genaue Werte (`geheime_werte`, `geheim_funde`): Kontonummer, Benutzerordner, Dateinamen und Spielername
   stehen im Monitor; die fertigen Dateien dürfen keinen dieser Werte enthalten.

Öffentlich werden nur gültige Aufnahmen. Was nach einem Neuladen verworfen ist, bleibt draußen.
"""

from __future__ import annotations

import json
import lzma
import re
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA = 1
SPIEL = "ck3"

# ---------------------------------------------------------------------------------------------------------------
# Privates erkennen

# Laufwerkspfade (ohne „https:/“), Benutzer- und Dokumentenordner, Steam-Ordner mit Kontonummer, der Ordner der
# Spielstände, Dateinamen von Spielständen, SteamID64. Dasselbe Muster steht in scripts/validate-data.mjs.
PRIVAT = re.compile(
    r"(?<![A-Za-z])[A-Za-z]:[\\/]|[\\/](?:Users|home)[\\/]|(?:Dokumente|Documents)[\\/]|\buserdata\b|\bsteamapps\b|"
    r"Steam[\\/]|save games|[^\s\"\\/]+\.ck3\b|(?<!\d)7656119\d{10}(?!\d)",
    re.I,
)
# Felder des Monitors, die nie veröffentlicht werden; als Schlüssel dürfen sie in den Daten nicht vorkommen.
PRIVATE_SCHLUESSEL = frozenset({"datei", "pfad", "letzte_datei", "spielername", "sha1", "kampagnenordner"})


def privat_funde(obj, pfad: str = "") -> list[str]:
    """Stellen (Schlüssel oder Text), die nach Pfad, Konto, Spielstand-Datei oder privatem Feld aussehen."""
    funde: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and (k in PRIVATE_SCHLUESSEL or PRIVAT.search(k)):
                funde.append(f"{pfad}/{k} (Schlüssel)")
            funde += privat_funde(v, f"{pfad}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            funde += privat_funde(v, f"{pfad}[{i}]")
    elif isinstance(obj, str) and PRIVAT.search(obj):
        funde.append(f"{pfad}: {obj[:60]}")
    return funde


def geheime_werte(aufnahmen: list[dict], infos: list[dict]) -> dict[str, set[str]]:
    """Die privaten Werte selbst, gelesen aus dem Monitor: Kontonummern, Benutzerordner, Dateinamen, Spielernamen.

    Sie bleiben im Speicher und dienen nur dem Vergleich mit den fertigen Dateien."""
    werte = {"kontonummer": set(), "benutzerordner": set(), "dateiname": set(), "spielername": set()}

    def pfad_auswerten(pfad) -> None:
        if not isinstance(pfad, str):
            return
        werte["kontonummer"].update(re.findall(r"userdata[\\/]+(\d{3,})", pfad, re.I))
        werte["benutzerordner"].update(re.findall(r"[\\/]Users[\\/]+([^\\/]+)", pfad, re.I))
        name = re.split(r"[\\/]", pfad)[-1]
        if name:
            werte["dateiname"].add(name)

    for info in infos:
        pfad_auswerten(info.get("letzte_datei"))
    for a in aufnahmen:
        datei = a.get("datei") or {}
        pfad_auswerten(datei.get("pfad"))
        if isinstance(datei.get("name"), str) and datei["name"]:
            werte["dateiname"].add(datei["name"])
        spielername = ((a.get("snapshot") or {}).get("kampagne") or {}).get("spielername")
        if isinstance(spielername, str) and spielername.strip():
            werte["spielername"].add(spielername.strip())
    # Der Dateiname ohne Endung zählt mit, wenn er wie ein Dateiname aussieht (Ziffer oder Unterstrich);
    # ein einzelnes Wort wie der Name eines Hauses darf im Text der Chronik stehen.
    for name in list(werte["dateiname"]):
        stamm = name.rsplit(".", 1)[0]
        if len(stamm) >= 6 and re.search(r"[\d_]", stamm):
            werte["dateiname"].add(stamm)
    return {art: {w for w in menge if len(w) >= 3} for art, menge in werte.items()}


def geheim_funde(text: str, werte: dict[str, set[str]]) -> list[str]:
    """Arten privater Werte, die in einem Text vorkommen. Die Werte selbst werden nie ausgegeben.

    Dateinamen zählen überall, wo sie stehen. Die Kontonummer zählt als eigene Zahl (nicht als Teil einer längeren),
    Spielername und Benutzerordner als ganzes Wort: „Anna“ trifft weder „Annahme“ noch „Johanna“."""
    grenzen = {"dateiname": ("", ""), "kontonummer": (r"(?<!\d)", r"(?!\d)")}
    funde = []
    for art, menge in werte.items():
        davor, danach = grenzen.get(art, (r"(?<!\w)", r"(?!\w)"))
        if any(re.search(davor + re.escape(wert) + danach, text, re.I) for wert in menge):
            funde.append(art)
    return funde


def repo_funde(root: Path, werte: dict[str, set[str]]) -> list[str]:
    """Dateien eines Ordners (ohne .git), die einen der privaten Werte enthalten: „Pfad: Art“."""
    funde = []
    for pfad in sorted(Path(root).rglob("*")):
        teile = pfad.relative_to(root).parts
        if not pfad.is_file() or {".git", "__pycache__", "node_modules", ".publish-cache"} & set(teile):
            continue
        text = pfad.read_bytes().decode("utf-8", errors="replace")
        funde += [f"{'/'.join(teile)}: {art}" for art in geheim_funde(text, werte)]
    return funde


# ---------------------------------------------------------------------------------------------------------------
# Erlaubnislisten: Felder einer Aufnahme, die veröffentlicht werden

SPIELER_FELDER = (
    "figur", "name", "anrede", "titel_name", "haupttitel", "stufe", "geburt", "alter", "weiblich", "haus", "haus_name",
    "dynastie", "dynastie_name", "kultur", "glaube", "regierung", "herrscher_seit", "gold", "prestige",
    "prestige_gesamt", "froemmigkeit", "froemmigkeit_gesamt", "einfluss", "einkommen", "stress", "gesundheit",
    "schrecken", "legitimitaet", "heeresstaerke", "aufgebot", "fertigkeiten", "eigenschaften", "gefangen", "erbe",
    "erbfolge", "lehnsherr", "vasallen", "titel", "domaene", "grafschaften_im_reich", "hauptstadt", "buendnisse",
    "waffenstillstaende",
    # seit CK3 1.21 (Kaufleute, Landlose): Art der Bindung an den Lehnsherrn oder Gönner, Ritus, Sitz, Tributpflichtige,
    # Gesetze (bei Kaufleuten etwa der Zweck der Gesellschaft)
    "lehnsherr_art", "ritus", "sitz", "tributpflichtige", "gesetze",
    # seit Leser 3 des Monitors: seit wann das Haus des Lehnsherrn oder Gönners den Vertrag hält (bei einem neuen
    # Vorgesetzten der Tag, an dem er begann) und die Art des Vertrags, wie das Spiel sie nennt
    "lehnsherr_seit", "lehnsherr_vertrag",
    # seit Leser 4 des Monitors: wo die Spielfigur am Tag der Aufnahme ist, ihr Reiseplan (Abreise, Ziele mit
    # Ankunft und geplantem Tag, Weg, Mitreisende, Auftrag), wer am selben Ort ist, ihre Aufträge mit Status und ihr
    # Hof mit Ämtern. Alles Spielinhalt; die Bestandteile gehen so durch, wie der Monitor sie führt.
    "aufenthalt", "reise", "am_ort", "auftraege", "hof",
)
FIGUR_FELDER = ("id", "name", "beiname", "weiblich", "geburt", "haus", "haus_name", "lebend", "tod", "todesursache",
                "ehepartner", "fruehere_ehepartner", "kinder", "verlobt", "eltern", "titel", "titel_name", "titel_stufe",
                "bezug", "eigenschaften")
TITEL_FELDER = ("id", "key", "name", "stufe", "art", "landlos", "rang", "inhaber", "seit", "lehnsherr_titel", "de_jure_titel",
                "erwerb")
KRIEG_FELDER = ("id", "name", "beginn", "angreifer", "verteidiger", "hauptangreifer", "hauptverteidiger", "kriegsgrund",
                "ziele", "anspruchsteller", "spieler_seite", "umfeld")
# Seit Leser 4: Unternehmungen (etwa ein Festmahl) mit Gastgeber, Gästen, Ort, Kosten und dem Protokoll des Spiels,
# dazu das Umfeld des Sitzes (Grafschaft, Kette der Herren, De-jure-Titel).
UNTERNEHMUNG_FELDER = ("id", "art", "name", "gastgeber", "gaeste", "ort", "angelegt", "beginn", "aktiv", "abgeschlossen",
                       "kosten", "abschnitte", "protokoll")
PROTOKOLL_FELDER = ("datum", "figur", "ziel", "titel", "text", "wirkung")
UMFELD_FELDER = ("grafschaft", "kette", "de_jure")
ERINNERUNG_FELDER = ("id", "art", "datum", "figur", "beteiligte", "titel", "grund")
HAUS_FELDER = ("id", "name", "oberhaupt", "gegruendet", "mitglieder_lebend", "einigkeit")
DYNASTIE_FELDER = ("id", "name", "oberhaupt", "ruhm", "ruhm_gesamt", "mitglieder_lebend", "haeuser")
DYNASTIE_HAUS_FELDER = ("id", "name", "oberhaupt", "mitglieder_lebend")
CHRONIK_FELDER = ("id", "nr", "art", "datum", "zeitraum", "text", "figuren", "quelle", "wichtig")
# Aus dem Block `datei` nur, wie gelesen wurde; Pfad, Name, Größe und Prüfsumme bleiben im Monitor.
LESUNG_FELDER = {"format": "format", "rakaly": "rakaly", "parser": "parser", "leser": "leser", "index_exakt": "index_exakt",
                 "ironman_laut_dateiname": "ironman"}
# Felder der Aufnahme, die hier bewusst fehlen: Verwaltung des Monitors und das Private.
BEKANNT_OHNE_VEROEFFENTLICHUNG = {
    "aufnahme": {"datei"},
    "snapshot": {"spiel", "format", "welt_quelle", "spieldatum_roh", "nicht_gefunden", "kriege_aktiv"},
    "kampagne": {"spielername"},
}
SNAPSHOT_FELDER = ("welt_id", "spieldatum", "spielversion", "start", "kampagne", "hinweise", "spieler", "figuren",
                   "titel", "kriege", "erinnerungen", "haus", "dynastie", "versionspruefung", "unternehmungen", "umfeld")
KAMPAGNE_FELDER = ("spielzeit_s", "erfolge_moeglich")

# Kennzahlen des Verlaufs: Schlüssel → Beschriftung. „Fehlt“ ist nicht 0: Ein fehlender Wert bleibt null.
KENNZAHLEN = {
    "gold": "Gold", "einkommen": "Einkommen pro Monat", "prestige": "Prestige", "prestige_gesamt": "Prestige gesamt",
    "froemmigkeit": "Frömmigkeit", "froemmigkeit_gesamt": "Frömmigkeit gesamt", "einfluss": "Einfluss",
    "heeresstaerke": "Heeresstärke", "aufgebot": "Aufgebot", "grafschaften_im_reich": "Grafschaften im Reich",
    "titel": "Titel der Spielfigur", "vasallen": "Vasallen", "hausmitglieder": "Lebende Hausmitglieder",
    "dynastie_ruhm": "Ruhm der Dynastie", "dynastie_ruhm_gesamt": "Ruhm der Dynastie gesamt", "stress": "Stress",
    "gesundheit": "Gesundheit", "schrecken": "Schrecken", "legitimitaet": "Legitimität",
}


def _auswahl(quelle: dict | None, felder) -> dict:
    return {f: quelle[f] for f in felder if f in (quelle or {})}


def _ohne_leeres(d: dict) -> dict:
    """Ohne null und leere Listen: In den Listen der Figuren und Titel heißt ein fehlendes Feld „kein Wert“."""
    return {k: v for k, v in d.items() if v is not None and v != [] and v != {}}


def unbekannte_felder(aufnahme_roh: dict) -> set[str]:
    """Felder des Monitors, die auf keiner Liste stehen und deshalb nicht veröffentlicht werden."""
    snap = aufnahme_roh.get("snapshot") or {}
    neu = {f for f in aufnahme_roh if f not in ("nr", "gelesen_um", "snapshot")} - BEKANNT_OHNE_VEROEFFENTLICHUNG["aufnahme"]
    neu |= {f"snapshot.{f}" for f in set(snap) - set(SNAPSHOT_FELDER) - BEKANNT_OHNE_VEROEFFENTLICHUNG["snapshot"]}
    neu |= {f"kampagne.{f}" for f in set(snap.get("kampagne") or {}) - set(KAMPAGNE_FELDER) - BEKANNT_OHNE_VEROEFFENTLICHUNG["kampagne"]}
    neu |= {f"spieler.{f}" for f in set(snap.get("spieler") or {}) - set(SPIELER_FELDER)}
    for teil, felder in (("haus", HAUS_FELDER), ("dynastie", DYNASTIE_FELDER)):
        neu |= {f"{teil}.{f}" for f in set(snap.get(teil) or {}) - set(felder)}
    for teil, felder in (("figuren", FIGUR_FELDER), ("titel", TITEL_FELDER)):
        for eintrag in (snap.get(teil) or {}).values():
            neu |= {f"{teil}.{f}" for f in set(eintrag) - set(felder)}
    for teil, felder in (("kriege", KRIEG_FELDER), ("erinnerungen", ERINNERUNG_FELDER)):
        for eintrag in snap.get(teil) or []:
            neu |= {f"{teil}.{f}" for f in set(eintrag) - set(felder)}
    for haus in (snap.get("dynastie") or {}).get("haeuser") or []:
        neu |= {f"dynastie.haeuser.{f}" for f in set(haus) - set(DYNASTIE_HAUS_FELDER)}
    for unternehmung in snap.get("unternehmungen") or []:
        neu |= {f"unternehmungen.{f}" for f in set(unternehmung) - set(UNTERNEHMUNG_FELDER)}
        for zeile in unternehmung.get("protokoll") or []:
            neu |= {f"unternehmungen.protokoll.{f}" for f in set(zeile) - set(PROTOKOLL_FELDER)}
    neu |= {f"umfeld.{f}" for f in set(snap.get("umfeld") or {}) - set(UMFELD_FELDER)}
    return neu


def unternehmung(roh: dict) -> dict:
    """Eine Unternehmung mit ihrem Protokoll, nur mit den genannten Feldern."""
    out = _auswahl(roh, UNTERNEHMUNG_FELDER)
    if isinstance(out.get("protokoll"), list):
        out["protokoll"] = [_auswahl(zeile, PROTOKOLL_FELDER) for zeile in out["protokoll"]]
    return out


def lesung(aufnahme_roh: dict) -> dict:
    """Wie der Monitor den Spielstand gelesen hat, ohne Pfad, Dateiname, Größe und Prüfsumme."""
    datei = aufnahme_roh.get("datei") or {}
    out = {ziel: datei[quelle] for quelle, ziel in LESUNG_FELDER.items() if datei.get(quelle) is not None}
    # Nur gezählt: Schlüssel, die rakaly nicht kennt, und Abschnitte, die es nur unter Platzhalternamen nennt
    for feld in ("unbekannte_schluessel", "platzhalter_schluessel"):
        if isinstance(datei.get(feld), list):
            out[feld] = len(datei[feld])
    return out


def aufnahme(aufnahme_roh: dict) -> dict:
    """Eine Aufnahme für die Seite: Stand der Spielfigur, der Figuren und der Titel zum Spieldatum."""
    snap = aufnahme_roh.get("snapshot") or {}
    dynastie = _auswahl(snap.get("dynastie"), DYNASTIE_FELDER)
    if isinstance(dynastie.get("haeuser"), list):
        dynastie["haeuser"] = [_auswahl(h, DYNASTIE_HAUS_FELDER) for h in dynastie["haeuser"]]
    out = {
        "schema": SCHEMA,
        "nr": aufnahme_roh.get("nr"),
        "world_id": snap.get("welt_id"),
        "spieldatum": snap.get("spieldatum"),
        "spielversion": snap.get("spielversion"),
        "start": snap.get("start"),
        "gespeichert_um": (aufnahme_roh.get("datei") or {}).get("geaendert"),
        "gelesen_um": aufnahme_roh.get("gelesen_um"),
        "lesung": lesung(aufnahme_roh),
        "lesestand": _auswahl(snap.get("versionspruefung"), ("stand", "text")),
        "kampagne": _auswahl(snap.get("kampagne"), KAMPAGNE_FELDER),
        "hinweise": list(snap.get("hinweise") or []),
        "spieler": _auswahl(snap.get("spieler"), SPIELER_FELDER) if snap.get("spieler") else None,
        "haus": _auswahl(snap.get("haus"), HAUS_FELDER) if snap.get("haus") else None,
        "dynastie": dynastie or None,
        "kriege": [_auswahl(k, KRIEG_FELDER) for k in snap.get("kriege") or []],
        "erinnerungen": [_auswahl(e, ERINNERUNG_FELDER) for e in snap.get("erinnerungen") or []],
        "figuren": {str(k): _ohne_leeres(_auswahl(f, FIGUR_FELDER)) for k, f in (snap.get("figuren") or {}).items()},
        "titel": {str(k): _ohne_leeres(_auswahl(t, TITEL_FELDER)) for k, t in (snap.get("titel") or {}).items()},
    }
    # Seit Leser 4; ältere Aufnahmen kennen diese Blöcke nicht und bleiben, wie sie waren
    if "unternehmungen" in snap:
        out["unternehmungen"] = [unternehmung(u) for u in snap.get("unternehmungen") or []]
    if "umfeld" in snap:
        out["umfeld"] = _auswahl(snap.get("umfeld"), UMFELD_FELDER) if snap.get("umfeld") else None
    return out


def verlauf_punkt(aufnahme_roh: dict) -> dict:
    """Kennzahlen einer Aufnahme für den Verlauf; die Spielfigur steht dabei, weil sie mit dem Erben wechselt."""
    snap = aufnahme_roh.get("snapshot") or {}
    p, haus, dynastie = snap.get("spieler") or {}, snap.get("haus") or {}, snap.get("dynastie") or {}
    werte = {k: p.get(k) for k in KENNZAHLEN if k in SPIELER_FELDER and k not in ("titel", "vasallen")}
    werte["titel"] = len(p.get("titel") or []) if p else None
    werte["vasallen"] = len(p.get("vasallen") or []) if p else None
    werte["hausmitglieder"] = haus.get("mitglieder_lebend")
    werte["dynastie_ruhm"] = dynastie.get("ruhm")
    werte["dynastie_ruhm_gesamt"] = dynastie.get("ruhm_gesamt")
    return {"nr": aufnahme_roh.get("nr"), "spieldatum": snap.get("spieldatum"), "figur": p.get("figur"),
            "name": p.get("name"), "spielzeit_s": (snap.get("kampagne") or {}).get("spielzeit_s"),
            **{k: werte.get(k) for k in KENNZAHLEN}}


def chronik_eintrag(e: dict) -> dict:
    return {f: e.get(f) for f in CHRONIK_FELDER}


def json_bytes(obj: dict, je_zeile: tuple[str, ...] = ()) -> bytes:
    """Gleicher Inhalt ergibt gleiche Bytes: Unveränderte Dateien erscheinen in keinem Commit.

    Die unter `je_zeile` genannten Listen und Tabellen stehen mit einem Eintrag je Zeile; so bleibt eine
    Aufnahme mit vielen Figuren klein und ein Vergleich zweier Stände lesbar."""
    kompakt = lambda v: json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    teile = []
    for k, v in obj.items():
        if k in je_zeile and isinstance(v, list) and v:
            inhalt = "[\n" + ",\n".join("  " + kompakt(e) for e in v) + "\n ]"
        elif k in je_zeile and isinstance(v, dict) and v:
            inhalt = "{\n" + ",\n".join("  " + kompakt(str(kk)) + ":" + kompakt(vv) for kk, vv in v.items()) + "\n }"
        else:
            inhalt = json.dumps(v, ensure_ascii=False, indent=1).replace("\n", "\n ")
        teile.append(" " + kompakt(str(k)) + ": " + inhalt)
    return ("{\n" + ",\n".join(teile) + "\n}\n").encode("utf-8")


# ---------------------------------------------------------------------------------------------------------------
# Eine Welt des Monitors lesen

@dataclass
class Welt:
    ordner: Path
    info: dict                      # welt.json des Monitors (enthält Privates: nur über index() nach außen)
    aufnahmen: list[dict]           # alle Aufnahmen in Lesereihenfolge, auch verworfene
    chronik: list[dict]
    verworfen: set = field(default_factory=set)

    @property
    def welt_id(self) -> str | None:
        return self.info.get("welt_id")

    @property
    def gueltig(self) -> list[dict]:
        return [a for a in self.aufnahmen if a.get("nr") not in self.verworfen]


def _zeilen(pfad: Path) -> list[dict]:
    """Gültige JSON-Zeilen einer Datei (auch gepackt als .xz); eine abgebrochene letzte Zeile wird übergangen."""
    if pfad.is_file():
        roh = pfad.read_bytes()
    elif pfad.with_name(pfad.name + ".xz").is_file():
        roh = lzma.decompress(pfad.with_name(pfad.name + ".xz").read_bytes())
    else:
        return []
    out = []
    for zeile in roh.splitlines():
        try:
            wert = json.loads(zeile.decode("utf-8"))
        except ValueError:
            continue
        if isinstance(wert, dict):
            out.append(wert)
    return out


def welt_lesen(ordner: Path) -> Welt:
    """Aufnahmen, Chronik und Weltdaten eines Ordners `daten/ck3/<welt>/`.

    Verworfen sind die Aufnahmen, die eine Chronikzeile der Art `neuladen` unter `verworfene_messungen` nennt:
    Springt das Spieldatum zurück, gelten die späteren Aufnahmen nicht mehr (so führt es der Monitor)."""
    ordner = Path(ordner)
    try:
        info = json.loads((ordner / "welt.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        info = {}
    aufnahmen = [a for a in _zeilen(ordner / "daten.jsonl") if a.get("nr") is not None]
    chronik = _zeilen(ordner / "chronik.jsonl")
    verworfen = {nr for e in chronik if e.get("art") == "neuladen" for nr in e.get("verworfene_messungen") or ()}
    return Welt(ordner, info if isinstance(info, dict) else {}, aufnahmen, chronik, verworfen)


def welt_infos(monitor: Path) -> list[tuple[Path, dict]]:
    """Ordner und welt.json aller CK3-Welten des Monitors."""
    out = []
    for pfad in sorted((Path(monitor) / "daten" / SPIEL).glob("*/welt.json")):
        try:
            info = json.loads(pfad.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(info, dict) and info.get("welt_id"):
            out.append((pfad.parent, info))
    return out


def welt_finden(monitor: Path, welt_id: str) -> Path | None:
    return next((ordner for ordner, info in welt_infos(monitor) if info.get("welt_id") == welt_id), None)


def welten_suchen(monitor: Path, suche: dict | None) -> list[Welt]:
    """Welten, die zu den Angaben unter „suche“ in data/monitor-sources.json passen.

    `angelegt_ab` (Tag, an dem der Monitor die Welt zum ersten Mal gelesen hat), `spielversion` (Anfang der
    Versionsnummer der letzten gültigen Aufnahme), `name` (Teil des Weltnamens) und `start` (Startdatum der Partie)."""
    suche = suche or {}
    treffer = []
    for ordner, info in welt_infos(monitor):
        if suche.get("angelegt_ab") and (info.get("angelegt") or "")[:10] < suche["angelegt_ab"]:
            continue
        if suche.get("name") and suche["name"].lower() not in (info.get("name") or "").lower():
            continue
        welt = welt_lesen(ordner)
        letzte = (welt.gueltig[-1].get("snapshot") or {}) if welt.gueltig else {}
        if suche.get("spielversion") and not (letzte.get("spielversion") or "").startswith(suche["spielversion"]):
            continue
        if suche.get("start") and letzte.get("start") != suche["start"]:
            continue
        if welt.gueltig:
            treffer.append(welt)
    return treffer


# ---------------------------------------------------------------------------------------------------------------
# Dateien für saves/<lauf>/data/monitor/

def index(welt: Welt, gueltig: list[dict], chronik: list[dict]) -> dict:
    snaps = [a.get("snapshot") or {} for a in gueltig]
    daten = sorted(s["spieldatum"] for s in snaps if s.get("spieldatum"))
    gespeichert = sorted(g for g in ((a.get("datei") or {}).get("geaendert") for a in gueltig) if g)
    gelesen = sorted(a["gelesen_um"] for a in gueltig if a.get("gelesen_um"))
    letzte = snaps[-1] if snaps else {}
    return {
        "schema": SCHEMA,
        "world_id": welt.welt_id,
        "welt": _ohne_leeres({"name": welt.info.get("name"), "quelle": welt.info.get("welt_quelle"), "start": letzte.get("start")}),
        "aufnahmen": len(gueltig),
        "verworfen": len(welt.aufnahmen) - len(gueltig),
        "neuladen": sum(1 for e in welt.chronik if e.get("art") == "neuladen"),
        "spieldatum_von": daten[0] if daten else None,
        "spieldatum_bis": daten[-1] if daten else None,
        "gespeichert_von": gespeichert[0] if gespeichert else None,
        "gespeichert_bis": gespeichert[-1] if gespeichert else None,
        "gelesen_bis": gelesen[-1] if gelesen else None,
        "spielversionen": sorted({s["spielversion"] for s in snaps if s.get("spielversion")}),
        "lesestand": _auswahl(letzte.get("versionspruefung"), ("stand", "text")),
        "verlauf": "verlauf.json",
        "chronik": "chronik.json",
        "chronik_eintraege": len(chronik),
        "letzte": aufnahme_datei(gueltig[-1]) if gueltig else None,
        "liste": [{"nr": a.get("nr"), "spieldatum": (a.get("snapshot") or {}).get("spieldatum"),
                   "gespeichert_um": (a.get("datei") or {}).get("geaendert"),
                   "spielversion": (a.get("snapshot") or {}).get("spielversion"),
                   "lesestand": ((a.get("snapshot") or {}).get("versionspruefung") or {}).get("stand"),
                   "aufnahme": aufnahme_datei(a)} for a in gueltig],
    }


def aufnahme_datei(aufnahme_roh: dict) -> str:
    return f"aufnahmen/aufnahme-{int(aufnahme_roh['nr']):04d}.json"


def bauen(welt: Welt) -> tuple[dict[str, bytes], dict]:
    """Alle Dateien einer Welt für `data/monitor/` (Pfad relativ dazu → Inhalt) und der Index als Wörterbuch."""
    gueltig = welt.gueltig
    nummern = {a.get("nr") for a in gueltig}
    chronik = [chronik_eintrag(e) for e in welt.chronik
               if e.get("art") != "neuladen" and not e.get("verworfen") and e.get("nr") in nummern]
    idx = index(welt, gueltig, chronik)
    dateien = {
        "index.json": json_bytes(idx, je_zeile=("liste",)),
        "verlauf.json": json_bytes({"schema": SCHEMA, "world_id": welt.welt_id, "kennzahlen": KENNZAHLEN,
                                    "punkte": [verlauf_punkt(a) for a in gueltig]}, je_zeile=("punkte",)),
        "chronik.json": json_bytes({"schema": SCHEMA, "world_id": welt.welt_id, "eintraege": chronik}, je_zeile=("eintraege",)),
    }
    for a in gueltig:
        dateien[aufnahme_datei(a)] = json_bytes(aufnahme(a), je_zeile=("figuren", "titel", "kriege", "erinnerungen", "unternehmungen"))
    return dateien, idx


def pruefen(dateien: dict[str, bytes], werte: dict[str, set[str]]) -> list[str]:
    """Privates in den fertigen Dateien: Muster und Schlüssel (privat_funde), dann die genauen Werte (geheim_funde)."""
    funde = []
    for name, inhalt in dateien.items():
        text = inhalt.decode("utf-8")
        funde += [f"{name}{f}" for f in privat_funde(json.loads(text))[:5]]
        funde += [f"{name}: enthält {art} aus dem Monitor" for art in geheim_funde(text, werte)]
    return funde
