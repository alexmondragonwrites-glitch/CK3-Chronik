"""Faktenblatt je Kapitel aus den Aufnahmen des Paradox-Monitors.

    py -3 scripts/fakten.py --save erster-lauf --kapitel 1 --bis 0867-04-02
    py -3 scripts/fakten.py --save erster-lauf --kapitel 2 --von 0867-04-02 --bis 0867-12-02

`--bis` ist der Stichtag: das Spieldatum der letzten Aufnahme, die das Kapitel verwendet. `--von` ist der Stichtag
des Kapitels davor; ohne `--von` beginnt das Blatt mit der ersten Aufnahme der Partie. Geschrieben wird
`werkstatt/<lauf>/fakten/kapitel-N.md`.

Das Blatt nennt nur, was die Aufnahmen zeigen: den Stand der Spielfigur am Anfang und am Stichtag, die Kennzahlen
je Aufnahme, die Menschen um die Spielfigur, Haus, Titel und die Chronik des Monitors im Zeitraum. Gründe,
Wortlaute und Entscheidungen stehen in keinem Spielstand; sie kommen vom Spieler.

Liegt daneben ein Beiblatt `kapitel-N-beiblatt.md`, hängt das Skript es an. Das Beiblatt führt eine Sitzung von
Hand: Angaben des Spielers und Funde aus dem Spielstand, die in den Aufnahmen nicht stehen.

Die Werkstatt ist öffentlich. Das Blatt entsteht deshalb aus denselben gefilterten Aufnahmen wie die Dateien der
Seite (`monitor_daten.aufnahme`) und wird vor dem Schreiben auf Privates geprüft, das Beiblatt eingeschlossen.
Gleiche Aufnahmen und gleiches Beiblatt ergeben dasselbe Blatt, Byte für Byte; nach einem Neuaufbau der Welt im
Monitor erzeugt man es neu.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
ROOT = HIER.parent
sys.path.insert(0, str(HIER))
import monitor_daten as md  # noqa: E402

LEER = "—"
ZIFFERN = ("", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
# Bezüge, die eine Figur zu den Menschen um die Spielfigur machen (so nennt sie der Monitor)
UMFELD = ("ehepartner", "früherer ehepartner", "kind", "eltern", "geschwister", "haus", "lehnsherr", "erbe", "verbündeter",
          "vasall", "kerkermeister", "ehepartner im haus", "kind im haus")
WERTE = (("gold", "Gold"), ("einkommen", "Einkommen pro Monat"), ("prestige", "Prestige"), ("prestige_gesamt", "Prestige gesamt"),
         ("froemmigkeit", "Frömmigkeit"), ("froemmigkeit_gesamt", "Frömmigkeit gesamt"), ("einfluss", "Einfluss"),
         ("stress", "Stress"), ("gesundheit", "Gesundheit"), ("schrecken", "Schrecken"), ("legitimitaet", "Legitimität"),
         ("heeresstaerke", "Heeresstärke"), ("aufgebot", "Aufgebot"))
KURVE = ("gold", "einkommen", "prestige", "froemmigkeit", "einfluss", "stress", "gesundheit")


def roemisch(n: int) -> str:
    zehner, einer = divmod(n, 10)
    return "X" * zehner + ZIFFERN[einer] if 0 < n < 40 else str(n)


def zahl(wert, vorzeichen: bool = False) -> str:
    """Deutsche Schreibweise mit höchstens zwei Nachkommastellen; ein fehlender Wert bleibt eine Lücke."""
    if not isinstance(wert, (int, float)) or isinstance(wert, bool):
        return LEER
    gerundet = round(float(wert), 2)
    text = f"{abs(gerundet):,.2f}".rstrip("0").rstrip(".").replace(",", " ").replace(".", ",").replace(" ", ".")
    if gerundet < 0:
        return "−" + text
    return ("+" if vorzeichen and gerundet > 0 else "") + text


def datum(iso) -> str:
    """„0867-04-02“ → „2.4.867“."""
    try:
        jahr, monat, tag = str(iso).split("-")
        return f"{int(tag)}.{int(monat)}.{int(jahr)}"
    except ValueError:
        return LEER


def zeitpunkt(iso) -> str:
    """„2026-11-17T19:08:41+01:00“ → „17.11.2026, 19:08 Uhr“."""
    text = str(iso or "")
    if len(text) < 16:
        return LEER
    return f"{int(text[8:10])}.{int(text[5:7])}.{text[0:4]}, {text[11:16]} Uhr"


def spielzeit(sekunden) -> str:
    if not isinstance(sekunden, (int, float)):
        return LEER
    minuten, rest = divmod(int(sekunden), 60)
    return f"{minuten // 60}:{minuten % 60:02d} h" if minuten >= 60 else f"{minuten}:{rest:02d} min"


def alter(geburt, heute) -> str:
    try:
        gj, gm, gt = (int(x) for x in str(geburt).split("-"))
        hj, hm, ht = (int(x) for x in str(heute).split("-"))
    except ValueError:
        return LEER
    return str(hj - gj - ((hm, ht) < (gm, gt)))


def jahre(n) -> str:
    """„22 Jahre“, „1 Jahr“; ohne Angabe eine Lücke."""
    return LEER if n in (None, LEER) else f"{n} Jahr" + ("" if str(n) == "1" else "e")


def titel_text(tid, a: dict) -> str:
    """Titel so, wie die Aufnahme ihn nennt: Name, Stufe (oder der Vermerk, dass keine dasteht) und Schlüssel."""
    t = (a.get("titel") or {}).get(str(tid)) if tid is not None else None
    if not t:
        return LEER if tid is None else f"Titel {tid} (nicht in der Aufnahme)"
    stufe = t.get("stufe") or ("ohne Stufenname" + (f", Art `{t['art']}`" if t.get("art") else ""))
    return f"{t.get('name') or t.get('key')} ({stufe}, `{t.get('key')}`)"


def figur_text(fid, a: dict, ausfuehrlich: bool = False) -> str:
    """Name einer Figur mit Haus; ausführlich auch Geburt, Alter und der Titel, den die Aufnahme zu ihr nennt."""
    if fid is None:
        return LEER
    f = (a.get("figuren") or {}).get(str(fid))
    if not f:
        return f"Figur {fid} (nicht im Blick)"
    text = f.get("name") or f"Figur {fid}"
    if f.get("beiname"):
        text += f" {f['beiname']}"
    if f.get("haus_name"):
        text += f" ({f['haus_name']})"
    if not ausfuehrlich:
        return text
    teile = []
    if f.get("geburt"):
        teile.append(f"geboren {datum(f['geburt'])}, {jahre(alter(f['geburt'], a.get('spieldatum')))}")
    if f.get("lebend") is False:
        teile.append(f"gestorben {datum(f.get('tod'))}" + (f" ({f['todesursache']})" if f.get("todesursache") else ""))
    if f.get("titel"):
        teile.append("Titel: " + titel_text(f["titel"][0], a))
    elif f.get("titel_name"):
        teile.append(f"Titel: {f['titel_name']} ({f.get('titel_stufe') or 'ohne Stufenname'})")
    if f.get("eltern"):
        teile.append("Eltern im Blick: " + ", ".join(figur_text(e, a) for e in f["eltern"]))
    return text + (", " + ", ".join(teile) if teile else "")


def sitz_text(a: dict) -> str:
    sitz = (a.get("spieler") or {}).get("sitz")
    if not isinstance(sitz, dict):
        return LEER
    grafschaft = (a.get("titel") or {}).get(str(sitz.get("grafschaft")))
    return (sitz.get("ort") or LEER) + (f" ({grafschaft.get('stufe') or 'Titel'} {grafschaft.get('name')})" if grafschaft else "")


def gesetze(a: dict) -> dict[str, str]:
    """Gesetze der Spielfigur: Gruppe → Name."""
    return {g.get("gruppe_name") or g.get("gruppe") or "Gesetz": g.get("name") or g.get("schluessel") or LEER
            for g in (a.get("spieler") or {}).get("gesetze") or []}


def lesestand_der_version(welt: md.Welt, version) -> tuple[dict, int | None]:
    """Jüngster Lesestand einer Spielversion und die Nummer der Aufnahme, seit der er gilt.

    Der Monitor vermerkt in jeder Aufnahme, wie die Spielversion beim Lesen stand. Vergleicht der Spieler später Werte
    im Spiel, steht „bestätigt“ erst in den Aufnahmen danach; die früheren behalten ihren Vermerk bis zum Neuaufbau.
    Genannt wird die erste Aufnahme mit dem jüngsten Stand, damit das Blatt gleich bleibt, wenn weitere Aufnahmen folgen.
    """
    gleiche = sorted((a for a in welt.gueltig if (a.get("snapshot") or {}).get("spielversion") == version
                      and isinstance((a.get("snapshot") or {}).get("versionspruefung"), dict)), key=lambda a: a.get("nr") or 0)
    if not gleiche:
        return {}, None
    vermerk = gleiche[-1]["snapshot"]["versionspruefung"]
    seit = gleiche[-1]
    for a in reversed(gleiche):
        if a["snapshot"]["versionspruefung"].get("stand") != vermerk.get("stand"):
            break
        seit = a
    return {feld: vermerk[feld] for feld in ("stand", "text") if feld in vermerk}, seit.get("nr")


def tabelle(kopf: list[str], zeilen: list[list[str]]) -> list[str]:
    sauber = lambda zelle: str(zelle).replace("|", "/").replace(chr(10), " ")
    return (["| " + " | ".join(kopf) + " |", "|" + "|".join("---" for _ in kopf) + "|"]
            + ["| " + " | ".join(sauber(z) for z in zeile) + " |" for zeile in zeilen] + [""])


def auswahl(welt: md.Welt, von: str | None, bis: str) -> tuple[dict, list[dict]]:
    """Ausgangsstand und Aufnahmen des Kapitels (gefiltert), der Stichtag ist die letzte."""
    gueltig = sorted(welt.gueltig, key=lambda a: ((a.get("snapshot") or {}).get("spieldatum") or "", a.get("nr") or 0))
    tag = lambda a: (a.get("snapshot") or {}).get("spieldatum") or ""
    daten = sorted({tag(a) for a in gueltig})
    for grenze, name in ((bis, "--bis"), (von, "--von")):
        if grenze and grenze not in daten:
            raise SystemExit(f"{name} {grenze}: Zu diesem Spieldatum gibt es keine gültige Aufnahme. Vorhanden: {', '.join(daten) or 'keine'}")
    if von and von >= bis:
        raise SystemExit("--von muss vor --bis liegen.")
    im_kapitel = [a for a in gueltig if tag(a) <= bis and (not von or tag(a) > von)]
    anfang = [a for a in gueltig if tag(a) == von][-1] if von else im_kapitel[0]
    return md.aufnahme(anfang), [md.aufnahme(a) for a in im_kapitel]


def beiblatt_zeilen(text: str) -> list[str]:
    """Das Beiblatt als Abschnitt des Faktenblatts: Überschriften rücken eine Stufe tiefer, Codeblöcke bleiben, wie sie sind."""
    zeilen, im_code = [], False
    for zeile in text.replace(chr(13), "").strip().split(chr(10)):
        if zeile.lstrip().startswith("```"):
            im_code = not im_code
        zeilen.append("#" + zeile if zeile.startswith("#") and not im_code else zeile.rstrip())
    return zeilen


def blatt(welt: md.Welt, lauf: str, kapitel: int, von: str | None, bis: str, beiblatt: str | None = None) -> str:
    """Das Faktenblatt eines Kapitels als Markdown; `beiblatt` ist der Text des von Hand geführten Beiblatts."""
    anfang, aufnahmen = auswahl(welt, von, bis)
    stich = aufnahmen[-1]
    sa, ss = anfang.get("spieler") or {}, stich.get("spieler") or {}
    nummern = {a["nr"] for a in aufnahmen}
    z: list[str] = []

    # Lesestand: Es gilt der jüngste Vermerk des Monitors zur Spielversion des Stichtags, auch aus einer späteren Aufnahme.
    beim_lesen = stich.get("lesestand") or {}
    lesestand, lesestand_nr = lesestand_der_version(welt, stich.get("spielversion"))
    if not lesestand or lesestand.get("stand") == beim_lesen.get("stand"):
        lesestand, lesestand_nr = beim_lesen, stich.get("nr")
    vermerk = f"- **Lesestand:** {lesestand.get('stand') or LEER}. {lesestand.get('text') or ''}".rstrip()
    if lesestand_nr != stich.get("nr"):
        vermerk += (f" So vermerkt der Monitor seit der Aufnahme Nr. {lesestand_nr}; beim Lesen der Aufnahme "
                    f"Nr. {stich.get('nr')} galt „{beim_lesen.get('stand') or LEER}“.")

    z += [f"# Faktenblatt · {lauf} · Kapitel {roemisch(kapitel)}", "",
          "Erzeugt von `scripts/fakten.py` aus den Aufnahmen des Paradox-Monitors. Nicht von Hand ändern; nach einem Neuaufbau "
          "der Welt im Monitor neu erzeugen.", "",
          f"- **Welt:** `{welt.welt_id}`" + (f", im Monitor „{welt.info.get('name')}“" if welt.info.get("name") else ""),
          f"- **Zeitraum:** Spieldatum {datum(anfang.get('spieldatum'))} bis {datum(stich.get('spieldatum'))}",
          f"- **Stichtag:** Aufnahme Nr. {stich.get('nr')}, Spieldatum {datum(stich.get('spieldatum'))}, gespeichert am {zeitpunkt(stich.get('gespeichert_um'))}",
          vermerk]
    if lesestand.get("stand") != "bestätigt":
        z.append("- **Vorläufig:** Zahlen dieses Blatts gelten erst als belegt, wenn der Spieler Werte dieser Spielversion im Spiel verglichen hat.")
    for hinweis in sorted({h for a in aufnahmen for h in a.get("hinweise") or []}):
        z.append(f"- **Hinweis des Monitors:** {hinweis}")
    if beiblatt and beiblatt.strip():
        z.append(f"- **Beiblatt:** `kapitel-{kapitel}-beiblatt.md`, von Hand geführt und unten angehängt: Angaben des Spielers und Funde, "
                 "die in den Aufnahmen nicht stehen.")
    z.append("")

    z += ["## Aufnahmen des Zeitraums", ""]
    z += tabelle(["Nr.", "Spieldatum", "gespeichert", "Spielzeit der Partie", "Version", "Leser", "Lesestand beim Lesen"],
                 [[a.get("nr"), datum(a.get("spieldatum")), zeitpunkt(a.get("gespeichert_um")), spielzeit((a.get("kampagne") or {}).get("spielzeit_s")),
                   a.get("spielversion") or LEER, (a.get("lesung") or {}).get("leser") or LEER, (a.get("lesestand") or {}).get("stand") or LEER]
                  for a in ([anfang] if anfang["nr"] not in nummern else []) + aufnahmen])

    kopf_a = f"Anfang · Nr. {anfang.get('nr')} · {datum(anfang.get('spieldatum'))}"
    kopf_s = f"Stichtag · Nr. {stich.get('nr')} · {datum(stich.get('spieldatum'))}"
    z += ["## Spielfigur: Anfang und Stichtag", ""]

    def bindung(a: dict) -> str:
        sp = a.get("spieler") or {}
        if sp.get("lehnsherr") is None:
            return "keiner (unabhängig)"
        return f"{sp.get('lehnsherr_art') or 'Lehnsherr'}: {figur_text(sp['lehnsherr'], a, ausfuehrlich=True)}"

    def vertrag(a: dict) -> str:
        """Art des Vertrags, wie das Spiel sie nennt, und seit wann das Haus des Vorgesetzten ihn hält (ab Leser 3 des Monitors)."""
        sp = a.get("spieler") or {}
        teile = ([f"`{sp['lehnsherr_vertrag']}`"] if sp.get("lehnsherr_vertrag") else []) \
            + ([f"beim Haus des Vorgesetzten seit {datum(sp['lehnsherr_seit'])}"] if sp.get("lehnsherr_seit") else [])
        return ", ".join(teile) or LEER

    def ehe(a: dict) -> str:
        eigene = (a.get("figuren") or {}).get(str((a.get("spieler") or {}).get("figur"))) or {}
        return ", ".join(figur_text(f, a) for f in eigene.get("ehepartner") or []) or "unverheiratet"

    def buendnisse(a: dict) -> str:
        return "; ".join(figur_text(b.get("mit"), a) for b in (a.get("spieler") or {}).get("buendnisse") or []) or "keine"

    lage = [
        ("Name", lambda a: f"{(a.get('spieler') or {}).get('name') or LEER}, im Spiel „{(a.get('spieler') or {}).get('anrede') or LEER}“"),
        ("Geboren", lambda a: f"{datum((a.get('spieler') or {}).get('geburt'))}, {jahre((a.get('spieler') or {}).get('alter'))}"),
        ("Titel, wie das Spiel ihn nennt", lambda a: (a.get("spieler") or {}).get("titel_name") or LEER),
        ("Haupttitel", lambda a: titel_text((a.get("spieler") or {}).get("haupttitel"), a)),
        ("Regierung", lambda a: (a.get("spieler") or {}).get("regierung") or LEER),
        ("Kultur", lambda a: (a.get("spieler") or {}).get("kultur") or LEER),
        ("Glaube", lambda a: " · ".join(x for x in ((a.get("spieler") or {}).get("glaube"), (a.get("spieler") or {}).get("ritus")) if x) or LEER),
        ("Sitz", sitz_text),
        ("Lehnsherr oder Gönner", bindung),
        ("Erbe", lambda a: figur_text((a.get("spieler") or {}).get("erbe"), a, ausfuehrlich=True) if (a.get("spieler") or {}).get("erbe") is not None else "keiner bekannt"),
        ("Erbfolge", lambda a: ", ".join(figur_text(f, a) for f in (a.get("spieler") or {}).get("erbfolge") or []) or LEER),
        ("Ehe", ehe),
        ("Bündnisse", buendnisse),
        ("Vasallen", lambda a: str(len((a.get("spieler") or {}).get("vasallen") or []))),
        ("Tributpflichtige", lambda a: str(len((a.get("spieler") or {}).get("tributpflichtige") or []))),
        ("Titel in der Hand", lambda a: ", ".join(titel_text(t, a) for t in (a.get("spieler") or {}).get("titel") or []) or "keine"),
        ("In Haft", lambda a: (f"bei {figur_text(((a.get('spieler') or {}).get('gefangen') or {}).get('von'), a)} seit "
                               f"{datum(((a.get('spieler') or {}).get('gefangen') or {}).get('seit'))}") if (a.get("spieler") or {}).get("gefangen") else "nein"),
    ]
    if any((a.get("spieler") or {}).get(feld) for a in (anfang, stich) for feld in ("lehnsherr_seit", "lehnsherr_vertrag")):
        lage.insert([name for name, _ in lage].index("Lehnsherr oder Gönner") + 1, ("Vertrag mit Lehnsherr oder Gönner", vertrag))
    z += tabelle(["Angabe", kopf_a, kopf_s, "Vergleich"],
                 [[name, wert(anfang), wert(stich), "geändert" if wert(anfang) != wert(stich) else ""] for name, wert in lage])

    z += ["### Werte", ""]
    haus_a, haus_s = anfang.get("haus") or {}, stich.get("haus") or {}
    dyn_a, dyn_s = anfang.get("dynastie") or {}, stich.get("dynastie") or {}
    paare = [(name, sa.get(feld), ss.get(feld)) for feld, name in WERTE]
    paare += [("Lebende Hausmitglieder", haus_a.get("mitglieder_lebend"), haus_s.get("mitglieder_lebend")),
              ("Einigkeit des Hauses", haus_a.get("einigkeit"), haus_s.get("einigkeit")),
              ("Ruhm der Dynastie", dyn_a.get("ruhm"), dyn_s.get("ruhm")),
              ("Ruhm der Dynastie gesamt", dyn_a.get("ruhm_gesamt"), dyn_s.get("ruhm_gesamt"))]
    beide = lambda x, y: isinstance(x, (int, float)) and isinstance(y, (int, float))
    z += tabelle(["Wert", kopf_a, kopf_s, "Veränderung"],
                 [[name, zahl(x), zahl(y), zahl(y - x, vorzeichen=True) if beide(x, y) and round(y - x, 2) else (LEER if not beide(x, y) else "")]
                  for name, x, y in paare])
    z += ["Eine Lücke (—) heißt: Der Wert fehlt in der Aufnahme. Fehlt ist nicht 0.", ""]

    fa, fs = sa.get("fertigkeiten") or {}, ss.get("fertigkeiten") or {}
    if fa or fs:
        z += ["### Fertigkeiten", ""]
        z += tabelle(["Fertigkeit", kopf_a, kopf_s], [[k, zahl(fa.get(k)), zahl(fs.get(k))] for k in list(fs) + [k for k in fa if k not in fs]])
    ea, es = sa.get("eigenschaften") or [], ss.get("eigenschaften") or []
    z += ["### Eigenschaften", "", f"- Am Stichtag: {', '.join(es) or LEER}"]
    if ea != es:
        z += [f"- Am Anfang: {', '.join(ea) or LEER}",
              f"- Hinzugekommen: {', '.join(e for e in es if e not in ea) or 'nichts'}; weggefallen: {', '.join(e for e in ea if e not in es) or 'nichts'}"]
    z.append("")
    ga, gs = gesetze(anfang), gesetze(stich)
    if ga or gs:
        z += ["### Gesetze", ""]
        z += tabelle(["Gruppe", kopf_a, kopf_s, "Vergleich"],
                     [[g, ga.get(g, LEER), gs.get(g, LEER), "geändert" if ga.get(g) != gs.get(g) else ""] for g in list(gs) + [g for g in ga if g not in gs]])

    z += ["## Kennzahlen je Aufnahme", ""]
    namen = dict(WERTE)
    z += tabelle(["Nr.", "Spieldatum"] + [namen[k] for k in KURVE],
                 [[a.get("nr"), datum(a.get("spieldatum"))] + [zahl((a.get("spieler") or {}).get(k)) for k in KURVE]
                  for a in ([anfang] if anfang["nr"] not in nummern else []) + aufnahmen])

    z += ["## Menschen um die Spielfigur am Stichtag", ""]
    spielfigur = ss.get("figur")

    def bezuege(f: dict, a: dict) -> str:
        """Bezug zur Spielfigur in Worten; der Lehnsherr heißt so, wie die Aufnahme die Bindung nennt (etwa „Gönner“)."""
        worte = {"ehepartner": "Ehepartner", "früherer ehepartner": "Früherer Ehepartner", "kind": "Kind", "eltern": "Elternteil",
                 "geschwister": "Geschwister", "haus": "Hausmitglied", "lehnsherr": (a.get("spieler") or {}).get("lehnsherr_art") or "Lehnsherr",
                 "erbe": "Erbe", "verbündeter": "Verbündeter", "vasall": "Vasall", "kerkermeister": "Kerkermeister",
                 "ehepartner im haus": "Ehepartner im Haus", "kind im haus": "Kind im Haus"}
        eigene = set(f.get("bezug") or [])
        if "ehepartner" in eigene:                      # die eigene Ehe steht schon da
            eigene.discard("ehepartner im haus")
        if "kind" in eigene:
            eigene.discard("kind im haus")
        return ", ".join(worte[b] for b in UMFELD if b in eigene)

    umfeld = lambda a: {f.get("id"): f for f in (a.get("figuren") or {}).values()
                        if f.get("id") != (a.get("spieler") or {}).get("figur") and set(f.get("bezug") or ()) & set(UMFELD)}
    menschen = sorted(umfeld(stich).values(), key=lambda f: (min(UMFELD.index(b) for b in f["bezug"] if b in UMFELD), f.get("geburt") or "", f.get("id") or 0))
    for f in menschen:
        z.append(f"- **{bezuege(f, stich)}:** {figur_text(f.get('id'), stich, ausfuehrlich=True)}")
    if not menschen:
        z.append("- Niemand im Blick.")
    for fid, f in sorted(umfeld(anfang).items()):
        if fid not in umfeld(stich):
            z.append(f"- **Am Anfang {bezuege(f, anfang)}, am Stichtag nicht mehr:** {figur_text(fid, stich if str(fid) in (stich.get('figuren') or {}) else anfang, ausfuehrlich=True)}")
    z.append("")

    mitglieder = lambda n: LEER if not isinstance(n, int) else ("1 lebendes Mitglied" if n == 1 else f"{n} lebende Mitglieder")
    z += ["## Haus und Dynastie am Stichtag", "",
          f"- **Haus:** {haus_s.get('name') or LEER}, gegründet {datum(haus_s.get('gegruendet'))}, Oberhaupt {figur_text(haus_s.get('oberhaupt'), stich)}, "
          f"{mitglieder(haus_s.get('mitglieder_lebend'))}",
          f"- **Dynastie:** {dyn_s.get('name') or LEER}, Oberhaupt {figur_text(dyn_s.get('oberhaupt'), stich)}, {mitglieder(dyn_s.get('mitglieder_lebend'))}, "
          f"Häuser: {', '.join(h.get('name') or str(h.get('id')) for h in dyn_s.get('haeuser') or []) or LEER}", ""]

    kriege = [k for a in aufnahmen for k in a.get("kriege") or [] if k.get("spieler_seite")]
    waffenruhe = ss.get("waffenstillstaende") or []
    z += ["## Kriege und Waffenstillstände der Spielfigur", ""]
    gesehen = set()
    for k in kriege:
        if k.get("id") in gesehen:
            continue
        gesehen.add(k.get("id"))
        z.append(f"- **Krieg:** {k.get('name') or LEER}, seit {datum(k.get('beginn'))}, Seite der Spielfigur: {k.get('spieler_seite')}, Kriegsgrund: {k.get('kriegsgrund') or LEER}")
    for w in waffenruhe:
        z.append(f"- **Waffenstillstand** mit {figur_text(w.get('mit'), stich)} bis {datum(w.get('bis'))}, nach „{w.get('krieg') or LEER}“, Ergebnis: {w.get('ergebnis') or LEER}")
    if not kriege and not waffenruhe:
        z.append("- Keine im Zeitraum.")
    z.append("")

    eintraege = [md.chronik_eintrag(e) for e in welt.chronik
                 if e.get("art") != "neuladen" and not e.get("verworfen") and e.get("nr") in nummern]
    eintraege.sort(key=lambda e: (e.get("datum") or (e.get("zeitraum") or [None, None])[1] or "", e.get("nr") or 0))
    welt_art = lambda e: e.get("art") == "herrscher" or (e.get("art") == "krieg" and spielfigur not in (e.get("figuren") or []) and "Spielfigur" not in (e.get("text") or ""))

    def zeile(e: dict) -> str:
        zeitraum = e.get("zeitraum") or [None, None]
        if e.get("datum"):
            wann = datum(e["datum"])
        elif zeitraum[0] and zeitraum[1] and zeitraum[0] != zeitraum[1]:
            wann = f"zwischen {datum(zeitraum[0])} und {datum(zeitraum[1])}"
        else:
            wann = datum(zeitraum[1])
        quelle = f" ({e['quelle']})" if e.get("quelle") not in (None, "Vergleich") else ""
        return f"- {wann} · Nr. {e.get('nr')} · `{e.get('art')}` · {e.get('text')}{quelle}"

    z += ["## Chronik des Monitors im Zeitraum", "",
          "Ein Eintrag mit eigenem Datum stammt aus dem Spielstand (Geburt, Tod, Kriegsbeginn, Erinnerung, Beginn eines Vertrags). "
          "Alles andere hat der Monitor beim Vergleich zweier Aufnahmen gesehen und trägt deren Zeitraum.", ""]
    for titel, gruppe in (("Spielfigur und ihr Umfeld, mit eigenem Datum", [e for e in eintraege if not welt_art(e) and e.get("datum")]),
                          ("Spielfigur und ihr Umfeld, zwischen zwei Aufnahmen", [e for e in eintraege if not welt_art(e) and not e.get("datum")]),
                          ("Welt", [e for e in eintraege if welt_art(e)])):
        z += [f"### {titel}", ""] + ([zeile(e) for e in gruppe] or ["- Nichts im Zeitraum."]) + [""]

    z += ["## Was der Spielstand nicht zeigt", "",
          "- Gründe, Wortlaute von Ereignissen und Entscheidungen. Das Tagebuch erfindet dafür keine Ursachen; was der Spieler dazu sagt, "
          "geht als „Angabe des Spielers“ in die Chronik ein.",
          "- Verdecktes: echte Väter, Geheimnisse, Intrigen, Schwangerschaften, geheime Glauben anderer.",
          "- Titel „ohne Stufenname“: Der Spielstand nennt für sie keine Stufe. Bezeichnungen, die hier fehlen, stehen so nicht in den Daten.", ""]
    if beiblatt and beiblatt.strip():
        z += beiblatt_zeilen(beiblatt) + [""]
    return chr(10).join(z)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--save", required=True, help="Lauf (Kennung aus data/monitor-sources.json)")
    ap.add_argument("--kapitel", required=True, type=int, help="Nummer des Kapitels")
    ap.add_argument("--bis", required=True, help="Stichtag: Spieldatum der letzten Aufnahme des Kapitels (JJJJ-MM-TT)")
    ap.add_argument("--von", help="Stichtag des Kapitels davor (JJJJ-MM-TT); ohne Angabe ab der ersten Aufnahme")
    ap.add_argument("--monitor", default=str(ROOT.parent / "Paradox-Monitor"), help="Ordner des Paradox-Monitors")
    ap.add_argument("--ausgabe", help="Blatt in diese Datei schreiben statt nach werkstatt/<lauf>/fakten/")
    args = ap.parse_args(argv)
    for strom in (sys.stdout, sys.stderr):
        if hasattr(strom, "reconfigure"):
            strom.reconfigure(errors="replace")

    monitor = Path(args.monitor)
    quellen = [q for q in json.loads((ROOT / "data" / "monitor-sources.json").read_text(encoding="utf-8")) if q.get("save") == args.save]
    if not quellen or not quellen[0].get("world_id"):
        print(f"Lauf „{args.save}“ hat in data/monitor-sources.json keine Weltkennung.", file=sys.stderr)
        return 2
    ordner = md.welt_finden(monitor, quellen[0]["world_id"]) if (monitor / "daten").is_dir() else None
    if not ordner:
        print(f"Die Welt {quellen[0]['world_id']} liegt nicht im Paradox-Monitor unter {monitor}.", file=sys.stderr)
        return 2
    welt = md.welt_lesen(ordner)
    meta = json.loads((ROOT / "saves" / args.save / "data" / "meta.json").read_text(encoding="utf-8"))
    lauf = " · ".join(x for x in (meta.get("name"), meta.get("lauf")) if x)
    bei = ROOT / "werkstatt" / args.save / "fakten" / f"kapitel-{args.kapitel}-beiblatt.md"
    text = blatt(welt, lauf, args.kapitel, args.von, args.bis, bei.read_text(encoding="utf-8") if bei.is_file() else None)

    # Privates: Muster und die genauen Werte aus allen Welten des Monitors (wie beim Hochladen)
    infos, alle = [], []
    for pfad in (monitor / "daten").glob("*/*/welt.json"):
        try:
            infos.append(json.loads(pfad.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
        alle += md.welt_lesen(pfad.parent).aufnahmen
    funde = md.privat_funde({"blatt": text.split(chr(10))}) + [f"enthält {art} aus dem Monitor" for art in md.geheim_funde(text, md.geheime_werte(alle, [i for i in infos if isinstance(i, dict)]))]
    if funde:
        print("Abbruch, nichts geschrieben. Das Faktenblatt enthält Privates:", *funde[:8], sep=chr(10) + "  ", file=sys.stderr)
        return 4

    ziel = Path(args.ausgabe) if args.ausgabe else ROOT / "werkstatt" / args.save / "fakten" / f"kapitel-{args.kapitel}.md"
    inhalt = text.encode("utf-8")
    if ziel.exists() and ziel.read_bytes() == inhalt:
        print(f"{ziel.name}: unverändert.")
        return 0
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_bytes(inhalt)
    print(f"{ziel.name} geschrieben: Kapitel {roemisch(args.kapitel)}, Spieldatum bis {datum(args.bis)}, {len(text.split(chr(10)))} Zeilen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
