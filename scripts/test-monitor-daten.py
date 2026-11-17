"""Tests für monitor_daten.py und publish-monitor.py (laufen ohne Paradox-Monitor, auch in der GitHub-Prüfung).

Die Tests bauen sich einen kleinen Monitor-Ordner mit erfundenen Daten. Private Werte (Kontonummer, Pfad,
Dateiname, Spielername) sind erfunden und werden zur Laufzeit zusammengesetzt: Die Prüfung des Repos sucht genau
solche Muster und soll in dieser Datei nichts finden.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import lzma
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import fakten  # noqa: E402
import monitor_daten as md  # noqa: E402

_spec = importlib.util.spec_from_file_location("publish_monitor", HIER / "publish-monitor.py")
publish = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(publish)

KONTO = "".join(str(z) for z in (5, 5, 5, 0, 1, 2, 3, 4))
DATEINAME = "_".join(["probe" + "haus", "867", "iron" + "man"]) + "." + "ck" + "3"
PFAD = "\\".join(["C:", "Program Files (x86)", "Ste" + "am", "user" + "data", KONTO, "1158310", "remote", "save" + " games", DATEINAME])
SPIELERNAME = "Probe" + "spielerin"
WELT = "ck3:" + "-".join("ab" * n for n in (4, 2, 2, 2, 6))


def schnappschuss(spieldatum: str, gold: float = 10.0, figur: int = 1) -> dict:
    return {
        "spiel": "ck3", "format": 1, "welt_id": WELT, "welt_quelle": "playthrough_id", "spieldatum": spieldatum,
        "spieldatum_roh": spieldatum.replace("-", "."), "spielversion": "1.21.0", "start": "0867-01-01",
        "kampagne": {"spielername": SPIELERNAME, "spielzeit_s": 600, "erfolge_moeglich": True},
        "hinweise": [],
        "spieler": {"figur": figur, "name": "Adela", "anrede": "Meisterin Adela", "titel_name": "Die Probe-Gesellschaft",
                    "haupttitel": 7, "stufe": "Kaufmannsfamilie", "geburt": "0845-03-05", "alter": 22, "weiblich": True,
                    "haus": 3, "haus_name": "Probehaus", "gold": gold, "prestige": None, "titel": [7], "vasallen": [],
                    "erbe": 2, "buendnisse": [{"mit": 5, "ueber": [[1, 5]]}], "handelsposten": 4,
                    "gesetze": [{"schluessel": "company_purpose_artisan", "name": "Kunsthandwerker",
                                 "gruppe": "company_purpose", "gruppe_name": "Gesellschaftszweck"}]},
        "figuren": {
            "1": {"id": 1, "name": "Adela", "beiname": None, "weiblich": True, "geburt": "0845-03-05", "haus": 3,
                  "haus_name": "Probehaus", "lebend": True, "tod": None, "todesursache": None, "ehepartner": [],
                  "fruehere_ehepartner": [], "kinder": [2], "verlobt": None, "titel": [7], "bezug": ["spieler"],
                  "eltern": [], "titel_name": "Die Probe-Gesellschaft", "titel_stufe": "Kaufmannsfamilie",
                  "geheimnis": "nur im Monitor"},
            "2": {"id": 2, "name": "Bero", "weiblich": False, "geburt": "0866-01-01", "lebend": True, "bezug": ["kind"],
                  "eltern": [1], "kinder": [], "titel": []},
        },
        "titel": {"7": {"id": 7, "key": "c_merchant_probe", "name": "Die Probe-Gesellschaft", "stufe": "Kaufmannsfamilie",
                        "art": "kaufmannsfamilie", "landlos": True, "rang": 2, "inhaber": 1, "seit": "0867-01-01", "lehnsherr_titel": None,
                        "de_jure_titel": None}},
        "kriege": [{"id": 9, "name": "Probekrieg", "beginn": "0867-02-01", "angreifer": [1], "verteidiger": [5],
                    "hauptangreifer": 1, "hauptverteidiger": 5, "kriegsgrund": "Anspruch", "ziele": [7],
                    "anspruchsteller": 1, "spieler_seite": "Angreifer"}],
        "erinnerungen": [{"id": 4, "art": "married", "datum": "0867-01-07", "figur": 1, "beteiligte": {"spouse": 5},
                          "titel": None, "grund": None}],
        "haus": {"id": 3, "name": "Probehaus", "oberhaupt": 1, "gegruendet": "0867-01-01", "mitglieder_lebend": 2,
                 "einigkeit": 100.0},
        "dynastie": {"id": 3, "name": "Probehaus", "oberhaupt": 1, "ruhm": 1.5, "ruhm_gesamt": 20.0, "mitglieder_lebend": 2,
                     "haeuser": [{"id": 3, "name": "Probehaus", "oberhaupt": 1, "mitglieder_lebend": 2, "intern": "x"}]},
        "nicht_gefunden": [], "kriege_aktiv": [9],
        "versionspruefung": {"stand": "ungeprüft", "text": "Version 1.21.0 ist ungeprüft."},
    }


def aufnahme(nr: int, spieldatum: str, **kw) -> dict:
    return {"nr": nr, "gelesen_um": f"2026-11-17T19:0{nr}:00+01:00",
            "datei": {"pfad": PFAD, "name": DATEINAME, "groesse": 123456, "geaendert": f"2026-11-17T19:0{nr}:00+01:00",
                      "sha1": "0" * 40, "parser": "clausewitz.py 1", "leser": 2, "ironman_laut_dateiname": True,
                      "format": "binär, mit rakaly umgewandelt", "rakaly": "0.8.23", "unbekannte_schluessel": ["0x1"],
                      "platzhalter_schluessel": ["oscar_104", "jakob_121"], "index_exakt": True, "dauer_s": 4.0},
            "snapshot": schnappschuss(spieldatum, **kw)}


def zeile(art: str, nr: int, text: str, **kw) -> dict:
    return {"art": art, "text": text, "datum": None, "zeitraum": [None, "0867-01-01"], "figuren": [1], "quelle": "Vergleich",
            "wichtig": False, "nr": nr, "welt_id": WELT, "id": f"{art}{nr}", **kw}


def monitor_anlegen(basis: Path, gepackt: bool = False) -> Path:
    """Monitor mit einer Welt: drei Aufnahmen, die zweite nach einem Neuladen verworfen."""
    ordner = basis / "daten" / "ck3" / "probewelt_1234abcd"
    ordner.mkdir(parents=True)
    aufnahmen = [aufnahme(1, "0867-01-01", gold=10.0), aufnahme(2, "0867-06-01", gold=99.0), aufnahme(3, "0867-03-01", gold=12.5)]
    roh = "".join(json.dumps(a, ensure_ascii=False, separators=(",", ":")) + "\n" for a in aufnahmen).encode("utf-8")
    if gepackt:
        (ordner / "daten.jsonl.xz").write_bytes(lzma.compress(roh))
    else:
        (ordner / "daten.jsonl").write_bytes(roh + b'{"nr": 4, "abgebrochen')          # unfertige letzte Zeile
    chronik = [
        zeile("beginn", 1, "Aufzeichnung beginnt: Adela (Probehaus)."),
        zeile("titel", 2, "Titel erlangt: Grafschaft Irgendwo.", verworfen=True),
        zeile("neuladen", 3, "Neuladen erkannt.", verworfene_messungen=[2]),
        zeile("geburt", 3, "Geburt: Bero (Probehaus).", datum="0867-02-11"),
    ]
    (ordner / "chronik.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in chronik), encoding="utf-8")
    (ordner / "welt.json").write_text(json.dumps({
        "welt_id": WELT, "spiel": "ck3", "welt_quelle": "playthrough_id", "name": "Probehaus ab 867 (Meisterin Adela)",
        "zuletzt_gelesen": "2026-11-17T19:03:00+01:00", "letztes_spieldatum": "0867-03-01", "aufnahmen": 3,
        "letzte_datei": PFAD, "erstes_spieldatum": "0867-01-01", "angelegt": "2026-11-17T19:01:00+01:00"}), encoding="utf-8")
    return basis


class Privates(unittest.TestCase):
    def test_muster_finden_pfad_dateiname_und_felder(self):
        roh = aufnahme(1, "0867-01-01")
        funde = md.privat_funde(roh)
        for erwartet in ("/datei (Schlüssel)", "/datei/pfad", "/datei/name", "/datei/sha1 (Schlüssel)", "spielername (Schlüssel)"):
            self.assertTrue(any(erwartet in f for f in funde), (erwartet, funde))
        self.assertTrue(md.privat_funde({"letzte_datei": "x"}))
        self.assertTrue(md.privat_funde({"x": "D:/" + "Dokumente" + "/Paradox Interactive"}))
        self.assertTrue(md.privat_funde({"x": "siehe " + "7656119" + "8000000001"}))
        self.assertTrue(md.privat_funde({"x": ["im Ordner user" + "data"]}))

    def test_muster_lassen_die_chronik_durch(self):
        harmlos = {"world_id": WELT, "gelesen_um": "2026-11-17T18:50:14+01:00", "link": "https://example.org/a",
                   "text": "Krieg begonnen: Probekrieg. Angreifer: Adela (Probehaus). Dokumente und Urkunden folgen.",
                   "name": "Die von Probe-Gesellschaft", "key": "c_merchant_probe"}
        self.assertEqual(md.privat_funde(harmlos), [])

    def test_genaue_werte(self):
        werte = md.geheime_werte([aufnahme(1, "0867-01-01")], [{"letzte_datei": PFAD}])
        self.assertEqual(werte["kontonummer"], {KONTO})
        self.assertEqual(werte["spielername"], {SPIELERNAME})
        self.assertIn(DATEINAME, werte["dateiname"])
        self.assertIn(DATEINAME.rsplit(".", 1)[0], werte["dateiname"])           # Stamm mit Ziffern zählt mit
        self.assertEqual(md.geheim_funde(f"Konto {KONTO} am Rand", werte), ["kontonummer"])
        self.assertEqual(md.geheim_funde(f"gespielt von {SPIELERNAME.lower()}.", werte), ["spielername"])
        self.assertEqual(md.geheim_funde(f"Nummer 9{KONTO}9 und {SPIELERNAME}nen", werte), [])   # nur ganze Zahlen und Wörter
        self.assertEqual(md.geheim_funde(f"ordner_{KONTO}_x", werte), ["kontonummer"])
        self.assertEqual(md.geheim_funde(f"RIFF{DATEINAME}", werte), ["dateiname"])              # Dateinamen überall
        benutzer = md.geheime_werte([], [{"letzte_datei": "C:" + "\\Users\\" + "probemensch" + "\\Documents\\x"}])
        self.assertEqual(benutzer["benutzerordner"], {"probemensch"})
        wort = md.geheime_werte([{"datei": {"name": "Probehaus" + ".ck" + "3"}}], [])
        self.assertNotIn("Probehaus", wort["dateiname"])                         # ein bloßes Wort bleibt erlaubt


class Aufnahmen(unittest.TestCase):
    def test_aufnahme_ohne_privates(self):
        roh = aufnahme(1, "0867-01-01")
        a = md.aufnahme(roh)
        self.assertEqual(md.privat_funde(a), [])
        text = json.dumps(a, ensure_ascii=False)
        for weg in (KONTO, DATEINAME, SPIELERNAME, "sha1", "groesse", "geheimnis", "handelsposten", "kriege_aktiv", "intern"):
            self.assertNotIn(weg, text)
        self.assertEqual(a["lesung"], {"format": "binär, mit rakaly umgewandelt", "rakaly": "0.8.23", "parser": "clausewitz.py 1",
                                       "leser": 2, "index_exakt": True, "ironman": True, "unbekannte_schluessel": 1,
                                       "platzhalter_schluessel": 2})
        self.assertEqual(a["spieler"]["gesetze"][0]["name"], "Kunsthandwerker")   # Gesetze der Gesellschaft, seit CK3 1.21
        self.assertIs(a["titel"]["7"]["landlos"], True)
        self.assertNotIn("oscar_104", text)                                      # Platzhalternamen nur gezählt
        self.assertEqual(a["kampagne"], {"spielzeit_s": 600, "erfolge_moeglich": True})
        self.assertEqual(a["gespeichert_um"], "2026-11-17T19:01:00+01:00")
        self.assertEqual(a["spieler"]["titel_name"], "Die Probe-Gesellschaft")
        self.assertIsNone(a["spieler"]["prestige"])                              # „fehlt“ bleibt null, wird nicht 0
        self.assertEqual(a["figuren"]["1"], {"id": 1, "name": "Adela", "weiblich": True, "geburt": "0845-03-05", "haus": 3,
                                             "haus_name": "Probehaus", "lebend": True, "kinder": [2], "titel": [7],
                                             "titel_name": "Die Probe-Gesellschaft", "titel_stufe": "Kaufmannsfamilie",
                                             "bezug": ["spieler"]})
        self.assertEqual(a["titel"]["7"]["art"], "kaufmannsfamilie")
        self.assertEqual(a["dynastie"]["haeuser"], [{"id": 3, "name": "Probehaus", "oberhaupt": 1, "mitglieder_lebend": 2}])

    def test_unbekannte_felder_werden_gemeldet(self):
        self.assertEqual(md.unbekannte_felder(aufnahme(1, "0867-01-01")),
                         {"spieler.handelsposten", "figuren.geheimnis", "dynastie.haeuser.intern"})
        bekannt = aufnahme(1, "0867-01-01")
        del bekannt["snapshot"]["spieler"]["handelsposten"], bekannt["snapshot"]["figuren"]["1"]["geheimnis"]
        del bekannt["snapshot"]["dynastie"]["haeuser"][0]["intern"]
        self.assertEqual(md.unbekannte_felder(bekannt), set())

    def test_verlauf(self):
        p = md.verlauf_punkt(aufnahme(3, "0867-03-01", gold=12.5))
        self.assertEqual((p["nr"], p["spieldatum"], p["figur"], p["name"], p["gold"]), (3, "0867-03-01", 1, "Adela", 12.5))
        self.assertIsNone(p["prestige"])
        self.assertEqual((p["titel"], p["vasallen"], p["hausmitglieder"], p["dynastie_ruhm_gesamt"]), (1, 0, 2, 20.0))
        self.assertEqual(set(md.KENNZAHLEN) - set(p), set())

    def test_json_bytes(self):
        obj = {"schema": 1, "figuren": {"1": {"id": 1, "name": "Ä"}, "2": {"id": 2}}, "liste": [{"a": 1}, {"b": [1, 2]}], "leer": [],
               "tief": {"x": [1, {"y": None}]}}
        roh = md.json_bytes(obj, je_zeile=("figuren", "liste"))
        self.assertEqual(json.loads(roh), obj)
        self.assertIn(b'\n  "1":{"id":1,"name":"\xc3\x84"},\n', roh)
        self.assertIn(b'\n  {"a":1},\n', roh)
        self.assertEqual(roh, md.json_bytes(json.loads(roh), je_zeile=("figuren", "liste")))    # bytegleich
        self.assertTrue(roh.endswith(b"\n}\n"))


class Welten(unittest.TestCase):
    def test_lesen_verworfen_und_bauen(self):
        for gepackt in (False, True):
            with self.subTest(gepackt=gepackt), tempfile.TemporaryDirectory() as tmp:
                monitor = monitor_anlegen(Path(tmp), gepackt)
                ordner = md.welt_finden(monitor, WELT)
                welt = md.welt_lesen(ordner)
                self.assertEqual([a["nr"] for a in welt.aufnahmen], [1, 2, 3])
                self.assertEqual(welt.verworfen, {2})
                self.assertEqual([a["nr"] for a in welt.gueltig], [1, 3])
                dateien, idx = md.bauen(welt)
                self.assertEqual(sorted(dateien), ["aufnahmen/aufnahme-0001.json", "aufnahmen/aufnahme-0003.json",
                                                   "chronik.json", "index.json", "verlauf.json"])
                self.assertEqual((idx["aufnahmen"], idx["verworfen"], idx["neuladen"]), (2, 1, 1))
                self.assertEqual((idx["spieldatum_von"], idx["spieldatum_bis"]), ("0867-01-01", "0867-03-01"))
                self.assertEqual(idx["letzte"], "aufnahmen/aufnahme-0003.json")
                self.assertEqual(idx["welt"], {"name": "Probehaus ab 867 (Meisterin Adela)", "quelle": "playthrough_id", "start": "0867-01-01"})
                chronik = json.loads(dateien["chronik.json"])["eintraege"]
                self.assertEqual([e["art"] for e in chronik], ["beginn", "geburt"])          # ohne Verworfenes und Neuladen
                self.assertNotIn("welt_id", chronik[0])
                verlauf = json.loads(dateien["verlauf.json"])["punkte"]
                self.assertEqual([p["gold"] for p in verlauf], [10.0, 12.5])               # 99.0 gehört zur verworfenen Aufnahme
                werte = md.geheime_werte(welt.aufnahmen, [welt.info])
                self.assertEqual(md.pruefen(dateien, werte), [])
                alles = b"".join(dateien.values()).decode("utf-8")
                for weg in (KONTO, DATEINAME, SPIELERNAME, "letzte_datei", "Program Files"):
                    self.assertNotIn(weg, alles)

    def test_pruefen_schlaegt_an(self):
        with tempfile.TemporaryDirectory() as tmp:
            welt = md.welt_lesen(md.welt_finden(monitor_anlegen(Path(tmp)), WELT))
            werte = md.geheime_werte(welt.aufnahmen, [welt.info])
            dateien, _ = md.bauen(welt)
            dateien["leck-1.json"] = md.json_bytes({"text": f"gespielt von {SPIELERNAME}"})
            dateien["leck-2.json"] = md.json_bytes({"datei": {"name": "x"}})
            dateien["leck-3.json"] = md.json_bytes({"ordner": KONTO})
            funde = md.pruefen(dateien, werte)
            self.assertTrue(any("leck-1.json" in f and "spielername" in f for f in funde), funde)
            self.assertTrue(any("leck-2.json" in f and "Schlüssel" in f for f in funde), funde)
            self.assertTrue(any("leck-3.json" in f and "kontonummer" in f for f in funde), funde)
            self.assertFalse(any(SPIELERNAME in f or KONTO in f for f in funde if "leck-3" in f or "enthält" in f))

    def test_suchen(self):
        with tempfile.TemporaryDirectory() as tmp:
            monitor = monitor_anlegen(Path(tmp))
            finden = lambda **suche: [w.welt_id for w in md.welten_suchen(monitor, suche)]
            self.assertEqual(finden(angelegt_ab="2026-11-17", spielversion="1.21"), [WELT])
            self.assertEqual(finden(angelegt_ab="2026-11-18"), [])
            self.assertEqual(finden(spielversion="1.19"), [])
            self.assertEqual(finden(name="probehaus", start="0867-01-01"), [WELT])
            self.assertEqual(finden(name="anderes haus"), [])
            self.assertIsNone(md.welt_finden(monitor, "ck3:unbekannt"))

    def test_repo_funde(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "docs").mkdir()
            (repo / ".git").mkdir()
            (repo / "docs" / "sauber.md").write_text("Adela führt die Probe-Gesellschaft.", encoding="utf-8")
            (repo / "docs" / "leck.md").write_text(f"Der Stand lag unter {KONTO}.", encoding="utf-8")
            (repo / "bild.webp").write_bytes(b"\x00RIFF" + DATEINAME.encode("utf-8") + b"\xff\xfe")
            (repo / ".git" / "config").write_text(SPIELERNAME, encoding="utf-8")
            werte = md.geheime_werte([aufnahme(1, "0867-01-01")], [])
            self.assertEqual(md.repo_funde(repo, werte), ["bild.webp: dateiname", "docs/leck.md: kontonummer"])


class Hochladen(unittest.TestCase):
    def test_schreiben_entfernt_verworfene_aufnahmen(self):
        with tempfile.TemporaryDirectory() as tmp:
            ziel = Path(tmp) / "monitor"
            alt = ziel / "aufnahmen" / "aufnahme-0002.json"
            alt.parent.mkdir(parents=True)
            alt.write_text("{}", encoding="utf-8")
            bleibt = ziel / "aufnahmen" / "aufnahme-0001.json"
            bleibt.write_bytes(b"{}\n")
            dateien = {bleibt: b"{}\n", ziel / "aufnahmen" / "aufnahme-0003.json": b"{}\n", ziel / "index.json": b"{}\n"}
            geaendert = publish.schreiben(dateien, ziel)
            self.assertEqual(sorted(p.name for p in geaendert), ["aufnahme-0002.json", "aufnahme-0003.json", "index.json"])
            self.assertFalse(alt.exists())
            self.assertEqual(publish.schreiben(dateien, ziel), [])                      # zweiter Lauf: nichts zu tun

    def test_welt_des_laufs(self):
        with tempfile.TemporaryDirectory() as tmp:
            monitor = monitor_anlegen(Path(tmp))
            quelle = {"save": "erster-lauf", "name": "Erster Lauf", "world_id": None, "suche": {"angelegt_ab": "2026-11-17"}}
            meldungen = io.StringIO()
            with contextlib.redirect_stdout(meldungen):
                self.assertEqual(publish.welt_des_laufs(quelle, monitor, None).welt_id, WELT)
                self.assertIsNone(publish.welt_des_laufs({**quelle, "suche": {"spielversion": "1.19"}}, monitor, None))
                self.assertIsNone(publish.welt_des_laufs(quelle, monitor, "ck3:unbekannt"))
                self.assertEqual(publish.welt_des_laufs({**quelle, "world_id": WELT, "suche": None}, monitor, None).welt_id, WELT)
            self.assertIn("noch kein Spielstand", meldungen.getvalue())
            self.assertIn("liegt nicht im Monitor", meldungen.getvalue())

    def test_mehrere_passende_welten(self):
        with tempfile.TemporaryDirectory() as tmp:
            monitor = monitor_anlegen(Path(tmp))
            zweite = monitor / "daten" / "ck3" / "zweitwelt_5678abcd"
            zweite.mkdir()
            andere = WELT[:-2] + "cd"
            roh = aufnahme(1, "0867-01-01")
            roh["snapshot"]["welt_id"] = andere
            (zweite / "daten.jsonl").write_text(json.dumps(roh) + chr(10), encoding="utf-8")
            (zweite / "welt.json").write_text(json.dumps({"welt_id": andere, "name": "Zweitwelt", "angelegt": "2026-11-18T08:00:00+01:00"}), encoding="utf-8")
            quelle = {"save": "erster-lauf", "name": "Erster Lauf", "world_id": None, "suche": {"angelegt_ab": "2026-11-17"}}
            meldungen = io.StringIO()
            with contextlib.redirect_stdout(meldungen):
                self.assertIsNone(publish.welt_des_laufs(quelle, monitor, None))            # keine Wahl ohne --welt
                self.assertEqual(publish.welt_des_laufs(quelle, monitor, andere).welt_id, andere)
            self.assertIn("Mehrere Welten passen", meldungen.getvalue())
            self.assertIn(andere, meldungen.getvalue())

    def test_spieldatum(self):
        self.assertEqual(publish.spieldatum("0875-02-13"), "13.2.875")
        self.assertEqual(publish.spieldatum(None), "?")

    def test_probelauf_mit_dem_echten_monitor(self):
        """Nur lokal: jede Welt des echten Monitors bauen und auf Privates prüfen. Geschrieben wird nichts."""
        monitor = HIER.parent.parent / "Paradox-Monitor"
        if not (monitor / "daten" / "ck3").is_dir():
            self.skipTest("kein Paradox-Monitor neben dem Repo")
        werte = publish.alle_geheimen_werte(monitor)
        self.assertTrue(werte["kontonummer"] and werte["dateiname"], "der Monitor nennt Kontonummer und Dateinamen")
        for ordner, info in md.welt_infos(monitor):
            welt = md.welt_lesen(ordner)
            if not welt.gueltig:
                continue
            dateien, idx = md.bauen(welt)
            self.assertEqual(md.pruefen(dateien, werte), [], info.get("name"))
            self.assertEqual(idx["aufnahmen"], len(welt.gueltig))


class Faktenblatt(unittest.TestCase):
    def test_schreibweisen(self):
        self.assertEqual([fakten.zahl(v) for v in (1300.4844, 0.699, 50.0, -8.0, None, True)], ["1.300,48", "0,7", "50", "−8", "—", "—"])
        self.assertEqual([fakten.zahl(v, vorzeichen=True) for v in (0.54, -17.26, 0)], ["+0,54", "−17,26", "0"])
        self.assertEqual((fakten.datum("0867-04-02"), fakten.datum(None)), ("2.4.867", "—"))
        self.assertEqual(fakten.zeitpunkt("2026-11-17T19:08:41+01:00"), "17.11.2026, 19:08 Uhr")
        self.assertEqual((fakten.spielzeit(1528), fakten.spielzeit(3600), fakten.spielzeit(None)), ("25:28 min", "1:00 h", "—"))
        self.assertEqual((fakten.alter("0845-01-01", "0867-01-01"), fakten.alter("0849-06-01", "0867-04-02")), ("22", "17"))
        self.assertEqual([fakten.roemisch(n) for n in (1, 4, 9, 14, 23)], ["I", "IV", "IX", "XIV", "XXIII"])

    def test_blatt_aus_gueltigen_aufnahmen(self):
        with tempfile.TemporaryDirectory() as tmp:
            welt = md.welt_lesen(md.welt_finden(monitor_anlegen(Path(tmp)), WELT))
            blatt = fakten.blatt(welt, "Probehaus", 1, None, "0867-03-01")
            self.assertEqual(blatt, fakten.blatt(welt, "Probehaus", 1, None, "0867-03-01"))          # gleiche Aufnahmen, gleiches Blatt
            self.assertTrue(blatt.startswith("# Faktenblatt · Probehaus · Kapitel I" + chr(10)))
            for erwartet in ("**Stichtag:** Aufnahme Nr. 3, Spieldatum 1.3.867, gespeichert am 17.11.2026, 19:03 Uhr",
                             "**Zeitraum:** Spieldatum 1.1.867 bis 1.3.867", "**Lesestand:** ungeprüft.", "**Vorläufig:**",
                             "| Gold | 10 | 12,5 | +2,5 |", "| Prestige | — | — | — |",
                             "| Gesellschaftszweck | Kunsthandwerker | Kunsthandwerker |  |",
                             "Die Probe-Gesellschaft (Kaufmannsfamilie, `c_merchant_probe`)",
                             "| Geboren | 5.3.845, 22 Jahre | 5.3.845, 22 Jahre |  |",
                             "- **Kind:** Bero, geboren 1.1.866, 1 Jahr, Eltern im Blick: Adela (Probehaus)",
                             "- **Krieg:** Probekrieg, seit 1.2.867, Seite der Spielfigur: Angreifer, Kriegsgrund: Anspruch",
                             "- 1.1.867 · Nr. 1 · `beginn` · Aufzeichnung beginnt: Adela (Probehaus).",
                             "- 11.2.867 · Nr. 3 · `geburt` · Geburt: Bero (Probehaus)."):
                self.assertIn(erwartet, blatt)
            for weg in ("99", "Grafschaft Irgendwo", "Neuladen", KONTO, DATEINAME, SPIELERNAME, "handelsposten", "geheimnis"):
                self.assertNotIn(weg, blatt)                                                          # Verworfenes, Privates, Unbekanntes
            self.assertEqual(md.privat_funde({"blatt": blatt.split(chr(10))}), [])
            self.assertEqual(md.geheim_funde(blatt, md.geheime_werte(welt.aufnahmen, [welt.info])), [])

    def test_lesestand_der_version_und_vertrag(self):
        """Spätere Bestätigung der Spielversion gilt auch für frühere Aufnahmen; der Vertrag mit dem Gönner (Leser 3) steht im Blatt."""
        with tempfile.TemporaryDirectory() as tmp:
            ordner = md.welt_finden(monitor_anlegen(Path(tmp)), WELT)
            aufnahmen = [aufnahme(1, "0867-01-01"), aufnahme(3, "0867-03-01", gold=12.5), aufnahme(4, "0867-09-01", gold=20.0),
                         aufnahme(5, "0867-12-01", gold=25.0)]
            for a, seit in zip(aufnahmen, ("0866-05-01", "0867-01-30", "0867-01-30", "0867-01-30")):
                a["snapshot"]["spieler"].update(lehnsherr=5, lehnsherr_art="Gönner", lehnsherr_seit=seit, lehnsherr_vertrag="tributary_merchant")
            for a in aufnahmen[2:]:                                                  # der Spieler hat nach der Aufnahme 3 im Spiel verglichen
                a["snapshot"]["versionspruefung"] = {"stand": "bestätigt", "text": "Version 1.21.0: im Spiel bestätigt."}
            (ordner / "daten.jsonl").write_text("".join(json.dumps(a, ensure_ascii=False) + chr(10) for a in aufnahmen), encoding="utf-8")
            welt = md.welt_lesen(ordner)

            gefiltert = md.aufnahme(aufnahmen[1])["spieler"]
            self.assertEqual((gefiltert["lehnsherr_seit"], gefiltert["lehnsherr_vertrag"]), ("0867-01-30", "tributary_merchant"))
            self.assertFalse({f for f in md.unbekannte_felder(aufnahmen[1]) if "lehnsherr" in f})

            blatt = fakten.blatt(welt, "Probehaus", 1, None, "0867-03-01")
            self.assertIn("- **Lesestand:** bestätigt. Version 1.21.0: im Spiel bestätigt. So vermerkt der Monitor seit der Aufnahme Nr. 4; "
                          "beim Lesen der Aufnahme Nr. 3 galt „ungeprüft“." + chr(10), blatt)                         # Nr. 4, auch wenn Nr. 5 folgt
            self.assertNotIn("**Vorläufig:**", blatt)
            self.assertIn("| 3 | 1.3.867 | 17.11.2026, 19:03 Uhr | 10:00 min | 1.21.0 | 2 | ungeprüft |", blatt)       # Vermerk beim Lesen bleibt stehen
            self.assertIn("| Vertrag mit Lehnsherr oder Gönner | `tributary_merchant`, beim Haus des Vorgesetzten seit 1.5.866 | "
                          "`tributary_merchant`, beim Haus des Vorgesetzten seit 30.1.867 | geändert |", blatt)
            spaeter = fakten.blatt(welt, "Probehaus", 2, "0867-03-01", "0867-09-01")
            self.assertIn("- **Lesestand:** bestätigt. Version 1.21.0: im Spiel bestätigt." + chr(10), spaeter)        # eigener Vermerk, ohne Verweis
            ohne = fakten.blatt(md.welt_lesen(md.welt_finden(monitor_anlegen(Path(tmp) / "zweiter"), WELT)), "Probehaus", 1, None, "0867-03-01")
            self.assertNotIn("Vertrag mit Lehnsherr oder Gönner", ohne)                                                # ältere Aufnahmen: keine leere Zeile

    def test_beiblatt_wird_angehaengt(self):
        """Das von Hand geführte Beiblatt steht am Ende des Faktenblatts, seine Überschriften eine Stufe tiefer."""
        with tempfile.TemporaryDirectory() as tmp:
            welt = md.welt_lesen(md.welt_finden(monitor_anlegen(Path(tmp)), WELT))
            ohne = fakten.blatt(welt, "Probehaus", 1, None, "0867-03-01")
            bei = chr(10).join(["# Beiblatt zu Kapitel I", "", "## Angaben der Spielerin", "", "- „weil der Hafen näher liegt“  ",
                                "", "```text", "# bleibt, wie es ist", "```", ""])
            mit = fakten.blatt(welt, "Probehaus", 1, None, "0867-03-01", bei.replace(chr(10), chr(13) + chr(10)))
            self.assertTrue(mit.endswith(chr(10).join(["## Beiblatt zu Kapitel I", "", "### Angaben der Spielerin", "",
                                                       "- „weil der Hafen näher liegt“", "", "```text", "# bleibt, wie es ist", "```", ""])))
            self.assertIn("- **Beiblatt:** `kapitel-1-beiblatt.md`, von Hand geführt und unten angehängt", mit)
            self.assertNotIn("Beiblatt", ohne)
            self.assertEqual(ohne, fakten.blatt(welt, "Probehaus", 1, None, "0867-03-01", "  " + chr(10)))            # leeres Beiblatt zählt nicht
            self.assertNotIn(chr(13), mit)

    def test_von_und_bis(self):
        with tempfile.TemporaryDirectory() as tmp:
            welt = md.welt_lesen(md.welt_finden(monitor_anlegen(Path(tmp)), WELT))
            anfang, aufnahmen = fakten.auswahl(welt, "0867-01-01", "0867-03-01")
            self.assertEqual((anfang["nr"], [a["nr"] for a in aufnahmen]), (1, [3]))                   # Aufnahme 2 ist verworfen
            anfang, aufnahmen = fakten.auswahl(welt, None, "0867-03-01")
            self.assertEqual((anfang["nr"], [a["nr"] for a in aufnahmen]), (1, [1, 3]))
            for von, bis in ((None, "0867-06-01"), (None, "0867-02-01"), ("0867-03-01", "0867-01-01")):
                with self.subTest(von=von, bis=bis), self.assertRaises(SystemExit):
                    fakten.auswahl(welt, von, bis)                                                     # verworfen, kein Stand, verkehrt herum


@unittest.skipUnless(shutil.which("git") and shutil.which("node"), "braucht git und node")
class EndeZuEnde(unittest.TestCase):
    """Das Hochlade-Skript in einer Kopie des Repos, mit erfundenem Monitor und einem Repo auf Zeit als „origin“."""

    def lauf(self, *args: str, cwd: Path) -> subprocess.CompletedProcess:
        umgebung = {**os.environ, "PYTHONUTF8": "1", "GIT_AUTHOR_NAME": "Probe", "GIT_AUTHOR_EMAIL": "probe@example.invalid",
                    "GIT_COMMITTER_NAME": "Probe", "GIT_COMMITTER_EMAIL": "probe@example.invalid"}
        return subprocess.run(list(args), cwd=cwd, env=umgebung, capture_output=True, text=True, encoding="utf-8")

    def test_hochladen_verwerfen_und_abbruch_bei_privatem(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            repo, origin = tmp / "repo", tmp / "origin.git"
            shutil.copytree(HIER.parent, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules", ".publish-cache"))
            monitor = monitor_anlegen(tmp / "monitor")
            git = lambda *a: self.lauf("git", *a, cwd=repo)
            skript = lambda *a: self.lauf(sys.executable, "-B", "scripts/publish-monitor.py", "--monitor", str(monitor), "--save", "probe-lauf", *a, cwd=repo)
            neu = self.lauf("node", "scripts/new-save.mjs", "--id", "probe-lauf", "--name", "Probehaus", "--started", "2026-11-17", "--version", "1.21", cwd=repo)
            self.assertEqual(neu.returncode, 0, neu.stderr)
            self.assertEqual(self.lauf("git", "init", "--bare", "-b", "main", str(origin), cwd=tmp).returncode, 0)
            for befehl in (("init", "-b", "main"), ("add", "-A"), ("commit", "-m", "Gerüst"), ("remote", "add", "origin", str(origin)),
                           ("push", "-u", "origin", "main")):
                self.assertEqual(git(*befehl).returncode, 0, befehl)
            ziel = repo / "saves" / "probe-lauf" / "data" / "monitor"

            # 1. Erster Upload: Welt gefunden und eingetragen, zwei gültige Aufnahmen, Commit bei origin
            r = skript("--yes")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("Hochgeladen: Probehaus bis 1.3.867 (2 Aufnahmen)", r.stdout)
            self.assertEqual(sorted(p.name for p in (ziel / "aufnahmen").iterdir()), ["aufnahme-0001.json", "aufnahme-0003.json"])
            quellen = json.loads((repo / "data" / "monitor-sources.json").read_text(encoding="utf-8"))
            self.assertEqual([q["world_id"] for q in quellen if q["save"] == "probe-lauf"], [WELT])
            self.assertEqual(json.loads((repo / "saves" / "probe-lauf" / "data" / "manifest.json").read_text(encoding="utf-8"))["monitor"],
                             "data/monitor/index.json")
            self.assertIn("Aufnahmen Probehaus bis 1.3.867", self.lauf("git", "log", "-1", "--format=%s", "main", cwd=origin).stdout)
            self.assertEqual(git("status", "--porcelain").stdout.strip(), "")
            hochgeladen = self.lauf("git", "show", "main:saves/probe-lauf/data/monitor/aufnahmen/aufnahme-0001.json", cwd=origin).stdout
            for weg in (KONTO, DATEINAME, SPIELERNAME):
                self.assertNotIn(weg, hochgeladen)

            # 2. Ohne neue Aufnahmen entsteht kein Commit
            stand = git("rev-parse", "HEAD").stdout
            r = skript("--yes")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("Keine neuen Aufnahmen.", r.stdout)
            self.assertEqual(git("rev-parse", "HEAD").stdout, stand)

            # 3. Neuladen im Spiel: Aufnahme 3 ist verworfen, ihre Datei verschwindet auch bei origin
            welt = monitor / "daten" / "ck3" / "probewelt_1234abcd"
            with (welt / "chronik.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(zeile("neuladen", 4, "Neuladen erkannt.", verworfene_messungen=[3])) + chr(10))
            r = skript("--yes")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((ziel / "aufnahmen" / "aufnahme-0003.json").exists())
            dateien = self.lauf("git", "ls-tree", "-r", "--name-only", "main", cwd=origin).stdout
            self.assertIn("saves/probe-lauf/data/monitor/aufnahmen/aufnahme-0001.json", dateien)
            self.assertNotIn("aufnahme-0003.json", dateien)
            self.assertEqual(json.loads((ziel / "index.json").read_text(encoding="utf-8"))["verworfen"], 2)

            # 4. Steht ein privater Wert irgendwo im Repo, wird nichts committet
            (repo / "werkstatt" / "notiz.md").write_text(f"gespielt von {SPIELERNAME}", encoding="utf-8")
            with (welt / "daten.jsonl").open("a", encoding="utf-8") as f:
                f.write(chr(10) + json.dumps(aufnahme(5, "0867-02-01", gold=11.0)) + chr(10))
            stand = git("rev-parse", "HEAD").stdout
            r = skript("--yes")
            self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
            self.assertIn("werkstatt/notiz.md: spielername", r.stderr)
            self.assertNotIn(SPIELERNAME, r.stdout + r.stderr)
            self.assertEqual(git("rev-parse", "HEAD").stdout, stand)


if __name__ == "__main__":
    unittest.main()
