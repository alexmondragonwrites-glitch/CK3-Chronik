// CK3-Chronik · Test der Datenprüfung: Schlägt validate-data.mjs an, wenn Privates oder Falsches im Repo liegt?
// Aufruf: node scripts/test-pruefung.mjs
// Der Test kopiert das Repo in einen Ordner auf Zeit, legt dort je Fall eine Datei hinein und erwartet einen Fehler.
// Private Werte sind erfunden und zur Laufzeit zusammengesetzt, damit diese Datei selbst sauber bleibt.
import { spawnSync } from "node:child_process";
import { appendFileSync, cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const KOPIE = mkdtempSync(join(tmpdir(), "ck3-chronik-pruefung-"));
const PRUEFUNG = join(ROOT, "scripts", "validate-data.mjs");

const KONTO = [5, 5, 5, 0, 1, 2, 3, 4].join("");
const SPIELSTAND = ["muster" + "haus", "1066", "iron" + "man"].join("_") + "." + "ck" + "3";
const PFAD = ["C:", "Program Files (x86)", "Ste" + "am", "user" + "data", KONTO, "1158310", "remote", "save" + " games", SPIELSTAND].join("\\");
const STEAM_ID = "7656119" + "8000000001";

const schreiben = (pfad, inhalt) => {
  mkdirSync(dirname(join(KOPIE, pfad)), { recursive: true });
  writeFileSync(join(KOPIE, pfad), typeof inhalt === "string" ? inhalt : JSON.stringify(inhalt, null, 1) + "\n", "utf8");
};
const lesen = (pfad) => readFileSync(join(KOPIE, pfad), "utf8");
const pruefen = () => {
  const r = spawnSync(process.execPath, [PRUEFUNG, "--root", KOPIE], { encoding: "utf8" });
  return { ok: r.status === 0, text: (r.stdout || "") + (r.stderr || "") };
};

let fehler = 0;
let faelle = 0;
function fall(name, einrichten, erwartet) {
  faelle += 1;
  const aufraeumen = einrichten();
  const r = pruefen();
  const treffer = !r.ok && erwartet.every((muster) => muster.test(r.text));
  if (!treffer) {
    fehler += 1;
    console.error(`FEHLT: ${name}\n  erwartet ${erwartet.join(" und ")}, die Prüfung meldet:\n  ${r.text.trim().split("\n").join("\n  ")}`);
  }
  aufraeumen();
  if (!pruefen().ok) throw new Error(`Nach dem Fall „${name}“ ist die Kopie nicht wieder sauber.`);
}
// Eine Datei auf Zeit; danach ist sie wieder weg
const datei = (pfad, inhalt) => () => { schreiben(pfad, inhalt); return () => rmSync(join(KOPIE, pfad)); };
// Eine vorhandene Datei auf Zeit ändern
const geaendert = (pfad, aendern) => () => { const alt = lesen(pfad); writeFileSync(join(KOPIE, pfad), aendern(alt), "utf8"); return () => writeFileSync(join(KOPIE, pfad), alt, "utf8"); };

try {
  cpSync(ROOT, KOPIE, { recursive: true, filter: (quelle) => !/[\\/](\.git|__pycache__|node_modules|\.publish-cache)$/.test(quelle) });
  const sauber = pruefen();
  if (!sauber.ok) throw new Error("Das Repo selbst besteht die Prüfung nicht:\n" + sauber.text);

  // Datenschutz: was der Paradox-Monitor an Privatem führt
  fall("welt.json des Monitors mit letzte_datei", datei("saves/erster-lauf/data/monitor/welt.json", { welt_id: "ck3:probe", letzte_datei: PFAD }),
    [/Rohdatei des Paradox-Monitors/, /private Felder des Monitors: \/letzte_datei/, /Pfad, eine Kontokennung/]);
  fall("Aufnahme mit dem Block datei (Pfad und Dateiname)", datei("saves/erster-lauf/data/leck-pfad.json", { nr: 1, datei: { pfad: PFAD, name: SPIELSTAND } }),
    [/private Felder des Monitors: \/datei, \/datei\/pfad/, /leck-pfad\.json: enthält etwas wie einen Pfad/]);
  fall("Spielername aus dem Spielstand", datei("saves/erster-lauf/data/leck-name.json", { kampagne: { spielername: "Jemand" } }),
    [/leck-name\.json: enthält private Felder des Monitors: \/kampagne\/spielername/]);
  fall("Dateiname eines Spielstands in den Daten", datei("data/leck-datei.json", { hinweis: "gelesen aus " + SPIELSTAND }),
    [/data\/leck-datei\.json: enthält etwas wie einen Pfad/]);
  fall("Dateiname eines Spielstands in der Werkstatt", datei("werkstatt/leck.md", "Stand aus " + SPIELSTAND + " gelesen.\n"),
    [/werkstatt\/leck\.md: enthält einen Steam-Ordner mit Kontonummer, eine Kontokennung oder den Namen eines Spielstands/]);
  fall("Steam-Ordner mit Kontonummer in einer Seite", datei("docs/leck.html", "<!doctype html><title>x</title><p>" + PFAD.replace(/\\/g, "/") + "</p>\n"),
    [/docs\/leck\.html: enthält einen Steam-Ordner mit Kontonummer/]);
  fall("SteamID64 in einem Text", datei("lore/leck.md", "Konto " + STEAM_ID + "\n"), [/lore\/leck\.md: enthält einen Steam-Ordner mit Kontonummer, eine Kontokennung/]);
  fall("Rohdaten des Monitors im Repo", datei("werkstatt/erster-lauf/daten.jsonl", "{}\n"), [/daten\.jsonl: Rohdatei des Paradox-Monitors/]);
  fall("Pfad in den Metadaten eines Bildes", () => {
    const pfad = "saves/erster-lauf/images/leck.png";
    mkdirSync(dirname(join(KOPIE, pfad)), { recursive: true });
    writeFileSync(join(KOPIE, pfad), Buffer.concat([Buffer.from([0x89, 0x50, 0x4e, 0x47]), Buffer.from(PFAD, "latin1")]));
    return () => rmSync(join(KOPIE, "saves/erster-lauf/images"), { recursive: true });
  }, [/leck\.png: Bild enthält einen Pfad/]);

  // Fremde Server und Schriften
  fall("Schrift von einem fremden Server", datei("leck-schrift.html", '<!doctype html><title>x</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X">\n'),
    [/leck-schrift\.html: lädt https:\/\/fonts\.googleapis\.com/]);
  fall("Stylesheet lädt von einem fremden Server", geaendert("assets/handschrift.css", (t) => t + '\n.x { background: url("https://example.org/bild.png"); }\n'),
    [/handschrift\.css: lädt https:\/\/example\.org/]);
  fall("Schriftdatei ohne passende Prüfsumme", () => {
    const pfad = join(KOPIE, "assets/fonts/texturina.woff2");
    const alt = readFileSync(pfad);
    appendFileSync(pfad, "x");
    return () => writeFileSync(pfad, alt);
  }, [/texturina\.woff2: steht nicht mit dieser Prüfsumme/]);

  // Register, Bücher und Kapitel
  const eintrag = { id: "erster-lauf-0001", recorded: "2026-11-17", kind: "fakt", category: "Titel", title: "Probe", description: "Probe.", source: "Q1" };
  fall("Registereintrag ohne Spieldatum", geaendert("saves/erster-lauf/data/events.json", () => JSON.stringify([eintrag])), [/erster-lauf-0001\): spieldatum/]);
  fall("Registereintrag mit Spieldatum und Zeitraum zugleich", geaendert("saves/erster-lauf/data/events.json",
    () => JSON.stringify([{ ...eintrag, spieldatum: "0867-01-01", zeitraum: [null, "0867-01-01"] }])), [/erster-lauf-0001\): spieldatum/]);
  fall("Registereintrag mit unbekannter Quelle", geaendert("saves/erster-lauf/data/events.json",
    () => JSON.stringify([{ ...eintrag, zeitraum: ["0867-01-01", "0867-03-01"], source: "Q999" }])), [/Quelle Q999 steht unter Quellen der Chronik nicht/]);
  // Unabhängig davon, wie viele Bücher und Kapitel die Chronik schon hat: Ein Buch 90 mit Kapitel 99 fällt aus der Zählung.
  fall("Buch und Kapitel außerhalb der Zählung", geaendert("saves/erster-lauf/chronik.html",
    (t) => t.replace("</main>", '<section class="hs-buch" id="buch-90"><article class="hs-kapitel" id="kapitel-99"></article></section></main>')),
  [/Buch 90 an Stelle \d+/, /Kapitel 99 an Stelle \d+/, /buecher nennt \d+ Bücher, die Chronik hat \d+/]);
  fall("Registereintrag zu einem Kapitel, das es nicht gibt", geaendert("saves/erster-lauf/data/events.json",
    () => JSON.stringify([{ ...eintrag, spieldatum: "0867-01-01", chapter: 99 }])), [/chapter 99 gibt es in der Chronik nicht/]);
  fall("Kapitel in meta.json, das die Chronik nicht hat, und Kapitel ohne Stichtag", () => {
    const zurueck = [
      geaendert("saves/erster-lauf/chronik.html", (t) => t.replace("</main>",
        '<section class="hs-buch" id="buch-90"><article class="hs-kapitel" id="kapitel-99"></article></section></main>'))(),
      geaendert("saves/erster-lauf/data/meta.json", (t) => {
        const m = JSON.parse(t);
        m.buecher = [...(m.buecher || []), { nr: 90, name: "Probe", kapitel: [{ nr: 98, spieldatum_bis: "0900-01-01" }] }];
        return JSON.stringify(m);
      })(),
    ];
    return () => zurueck.forEach((f) => f());
  }, [/buecher nennt die Kapitel [\d, ]*98, die Chronik hat [\d, ]*99/, /Kapitel 99 braucht seinen Stichtag/]);
  fall("Farbe, die das Stylesheet nicht kennt", geaendert("saves/erster-lauf/data/meta.json", (t) => t.replace('"status"', '"farbe": "rosa", "status"')),
    [/farbe rosa kennt assets\/handschrift\.css nicht/]);
  fall("Lauf ohne Karte im Portal", geaendert("index.html", (t) => t.replace('href="saves/erster-lauf/chronik.html"', 'href="#"')), [/Karte für den Lauf erster-lauf fehlt/]);

  // Figurenkanon: Die Seite gibt das Dossier im Wortlaut wieder; jede Abweichung fällt auf, gleich auf welcher Seite
  const chronik = lesen("saves/erster-lauf/chronik.html");
  const kanon = (/data-kanon="([^"]+)"/.exec(chronik) || [])[1];
  if (kanon) {
    const absatz = /<p>([^<]{40,})<\/p>/.exec(chronik.slice(chronik.indexOf("data-kanon=")))[1];
    fall("Figurenkanon auf der Seite umgeschrieben", geaendert("saves/erster-lauf/chronik.html", (t) => t.replace(absatz, "Anders erzählt. " + absatz.slice(12))),
      [/Figurenkanon weicht von lore\/[a-z0-9-]+\.md ab/]);
    fall("Dossier geändert, Seite nicht nachgezogen", geaendert(kanon, (t) => t.replace(absatz, absatz + " Ein neuer Satz des Spielers.")),
      [/Figurenkanon weicht von lore\/[a-z0-9-]+\.md ab/]);
    fall("Verweis auf ein Dossier, das es nicht gibt", geaendert("saves/erster-lauf/chronik.html", (t) => t.replace(`data-kanon="${kanon}"`, 'data-kanon="lore/niemand.md"')),
      [/data-kanon lore\/niemand\.md gibt es nicht/]);
  }

  // Aufnahmen: gültiger Bestand geht durch, eine verworfene Aufnahme im Ordner fällt auf
  const monitor = "saves/erster-lauf/data/monitor";
  const welt = "ck3:" + ["abababab", "abab", "abab", "abab", "abababababab"].join("-");
  const alteMeta = lesen("saves/erster-lauf/data/meta.json");
  const altesManifest = lesen("saves/erster-lauf/data/manifest.json");
  schreiben(`${monitor}/index.json`, { schema: 1, world_id: welt, aufnahmen: 1, verlauf: "verlauf.json", chronik: "chronik.json", chronik_eintraege: 0,
    liste: [{ nr: 1, spieldatum: "0867-01-01", aufnahme: "aufnahmen/aufnahme-0001.json" }] });
  schreiben(`${monitor}/aufnahmen/aufnahme-0001.json`, { schema: 1, nr: 1, world_id: welt, spieldatum: "0867-01-01" });
  schreiben(`${monitor}/verlauf.json`, { schema: 1, punkte: [{ nr: 1 }] });
  schreiben(`${monitor}/chronik.json`, { schema: 1, eintraege: [] });
  schreiben("saves/erster-lauf/data/meta.json", { ...JSON.parse(alteMeta), monitor: { world_id: welt } });
  schreiben("saves/erster-lauf/data/manifest.json", { latestReport: "chronik.html", monitor: "data/monitor/index.json" });
  const bestand = pruefen();
  if (!bestand.ok) throw new Error("Ein gültiger Bestand an Aufnahmen besteht die Prüfung nicht:\n" + bestand.text);
  fall("Verworfene Aufnahme liegt noch im Ordner", datei(`${monitor}/aufnahmen/aufnahme-0002.json`, { schema: 1, nr: 2, world_id: welt, spieldatum: "0867-06-01" }),
    [/aufnahme-0002\.json: steht nicht in index\.json/]);
  fall("Aufnahme passt nicht zum Index", geaendert(`${monitor}/aufnahmen/aufnahme-0001.json`, (t) => t.replace("0867-01-01", "0867-01-02")),
    [/aufnahme-0001\.json: nr, spieldatum oder world_id passen nicht/]);
  fall("Weltkennung in meta.json weicht ab", geaendert("saves/erster-lauf/data/meta.json", (t) => t.replace(welt, "ck3:andere")),
    [/monitor\.world_id passt nicht zu den Aufnahmen/]);
  fall("Verlauf mit falscher Zahl an Punkten", geaendert(`${monitor}/verlauf.json`, () => JSON.stringify({ schema: 1, punkte: [] })), [/verlauf\.json: 0 punkte, laut index\.json 1/]);
  rmSync(join(KOPIE, monitor), { recursive: true });
  writeFileSync(join(KOPIE, "saves/erster-lauf/data/meta.json"), alteMeta, "utf8");
  writeFileSync(join(KOPIE, "saves/erster-lauf/data/manifest.json"), altesManifest, "utf8");
} finally {
  rmSync(KOPIE, { recursive: true, force: true });
}

if (fehler) {
  console.error(`Test der Datenprüfung: ${fehler} von ${faelle} Fällen blieben unbemerkt.`);
  process.exit(1);
}
console.log(`Test der Datenprüfung ok: ${faelle} Fälle, jeder wurde gemeldet.`);
