// CK3-Chronik · Datenprüfung: Weltregister, Manifeste, Register, Bücher und Kapitel, Aufnahmen, Quellenanker,
// Schriften, fremde Server und Datenschutz.
// Aufruf: node scripts/validate-data.mjs [--root ORDNER]   (ohne Pakete; läuft auch in der GitHub-Prüfung)
import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const wurzel = process.argv.indexOf("--root");
const ROOT = wurzel > 0 ? process.argv[wurzel + 1] : join(dirname(fileURLToPath(import.meta.url)), "..");
const fehler = [];
const meldung = (datei, text) => fehler.push(`${datei}: ${text}`);

// Wie scripts/monitor_daten.py: Laufwerkspfade, Benutzer- und Dokumentenordner, Steam-Ordner, der Ordner der
// Spielstände, Dateinamen von Spielständen, SteamID64. Gilt für alle Daten (JSON unter data/ und saves/*/data/).
const PRIVAT = /(?<![A-Za-z])[A-Za-z]:[\\/]|[\\/](?:Users|home)[\\/]|(?:Dokumente|Documents)[\\/]|\buserdata\b|\bsteamapps\b|Steam[\\/]|save games|[^\s"\\/]+\.ck3\b|(?<!\d)7656119\d{10}(?!\d)/i;
// Felder des Paradox-Monitors, die nie veröffentlicht werden (datei.pfad, welt.json: letzte_datei, kampagne.spielername …)
const PRIVATE_SCHLUESSEL = new Set(["datei", "pfad", "letzte_datei", "spielername", "sha1", "kampagnenordner"]);
// Im ganzen Repo, auch in Texten und Skripten: Steam-Ordner mit Kontonummer, SteamID64, Dateiname eines Spielstands.
const KONTO = /userdata[\\/]+\d|(?<!\d)7656119\d{10}(?!\d)|[^\s"'`\\/<>*(„“]+\.ck3\b/i;
// Rohdateien des Monitors gehören nicht ins Repo, gleich in welchem Ordner.
const ROHDATEIEN = /(^|\/)(welt\.json|daten\.jsonl(\.xz)?|chronik\.jsonl|website\.json|einstellungen\.json)$|\.ck3$/i;
const TAG = /^\d{4}-\d{2}-\d{2}$/;
const WELT = /^ck3:[\w:.\-]+$/;
const FARBEN = ["blau", "rot", "gruen", "purpur", "schwarz", "gold"];

function lesen(pfad) {
  return readFileSync(join(ROOT, pfad), "utf8");
}

function json(pfad) {
  try {
    return JSON.parse(lesen(pfad));
  } catch (e) {
    meldung(pfad, `kein gültiges JSON (${e.message})`);
    return null;
  }
}

function dateien(ordner) {
  const voll = join(ROOT, ordner);
  if (!existsSync(voll)) return [];
  return readdirSync(voll).flatMap((name) => {
    if (name === ".git" || name === "node_modules" || name === "__pycache__" || name === ".publish-cache") return [];
    const rel = ordner ? `${ordner}/${name}` : name;
    return statSync(join(ROOT, rel)).isDirectory() ? dateien(rel) : [rel];
  });
}

function privateSchluessel(wert, pfad = "") {
  if (Array.isArray(wert)) return wert.flatMap((v, i) => privateSchluessel(v, `${pfad}[${i}]`));
  if (!wert || typeof wert !== "object") return [];
  return Object.entries(wert).flatMap(([k, v]) => [
    ...(PRIVATE_SCHLUESSEL.has(k) ? [`${pfad}/${k}`] : []),
    ...privateSchluessel(v, `${pfad}/${k}`),
  ]);
}

// Text einer Seite ohne Kommentare und Tags, Zeichenverweise aufgelöst, Leerraum vereinheitlicht
function klartext(seite) {
  return seite.replace(/<!--[\s\S]*?-->/g, " ").replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/\s+/g, " ");
}

// Wortlaut des Spielers in einem Dossier unter lore/: jeder Absatz und jede Überschrift, ohne den Rahmen der
// Werkstatt (Zitatblock am Anfang) und nur bis vor „## Offen“
function kanonAbsaetze(markdown) {
  const absaetze = [];
  for (const block of markdown.replace(/\r/g, "").split(/\n\s*\n/)) {
    const b = block.trim();
    if (!b || b.startsWith(">")) continue;
    if (/^##\s+Offen\b/.test(b)) break;
    absaetze.push(b.replace(/^#+\s+/, "").replace(/^\*+|\*+$/g, "").replace(/\s+/g, " "));
  }
  return absaetze;
}

// Spieldatum eines Registereintrags: eigenes Datum oder Zeitraum zwischen zwei Aufnahmen
function spielzeitOk(e) {
  if (e.spieldatum !== undefined) return TAG.test(e.spieldatum) && e.zeitraum === undefined;
  if (e.zeitraum !== undefined) {
    return Array.isArray(e.zeitraum) && e.zeitraum.length === 2 && TAG.test(e.zeitraum[1] || "")
      && (e.zeitraum[0] === null || (TAG.test(e.zeitraum[0]) && e.zeitraum[0] <= e.zeitraum[1]));
  }
  return typeof e.game_date_label === "string" && e.game_date_label.trim() !== "";
}

const css = existsSync(join(ROOT, "assets/handschrift.css")) ? lesen("assets/handschrift.css") : "";
if (!css) meldung("assets/handschrift.css", "fehlt");
const portal = existsSync(join(ROOT, "index.html")) ? lesen("index.html") : "";
if (!portal) meldung("index.html", "fehlt");

// 1. Weltregister
const welten = json("data/worlds.json");
const ids = new Set();
if (!Array.isArray(welten) || !welten.length) meldung("data/worlds.json", "braucht mindestens einen Lauf");
for (const w of welten || []) {
  const wo = `data/worlds.json (${w.id})`;
  if (!/^[a-z0-9-]+$/.test(w.id || "")) meldung(wo, "Kennung nur aus Kleinbuchstaben, Ziffern und Bindestrich");
  if (ids.has(w.id)) meldung(wo, "Kennung doppelt");
  ids.add(w.id);
  for (const feld of ["name", "path", "status", "started"]) if (!w[feld]) meldung(wo, `Feld ${feld} fehlt`);
  if (w.path !== `saves/${w.id}/`) meldung(wo, `path muss saves/${w.id}/ sein`);
  if (w.started && !TAG.test(w.started)) meldung(wo, "started im Format JJJJ-MM-TT");
  if (!["laufend", "abgeschlossen"].includes(w.status)) meldung(wo, "status ist laufend oder abgeschlossen");
  if (w.ended && !TAG.test(w.ended)) meldung(wo, "ended im Format JJJJ-MM-TT");
  for (const seite of ["index.html", w.page || "chronik.html"]) {
    if (!existsSync(join(ROOT, w.path || "", seite))) meldung(wo, `${w.path}${seite} fehlt`);
  }
  if (!portal.includes(`href="${w.path}${w.page || "chronik.html"}"`)) meldung("index.html", `Karte für den Lauf ${w.id} fehlt (bleibt ohne JavaScript stehen)`);
}

// 2. Je Lauf: meta, manifest, Quellenanker, Bücher und Kapitel, Register, Aufnahmen
for (const id of ids) {
  const basis = `saves/${id}`;
  const meta = json(`${basis}/data/meta.json`);
  if (meta && meta.id !== id) meldung(`${basis}/data/meta.json`, `id ist ${meta.id}, erwartet ${id}`);
  if (meta && meta.farbe && !FARBEN.includes(meta.farbe)) meldung(`${basis}/data/meta.json`, `farbe ${meta.farbe} kennt assets/handschrift.css nicht`);
  if (meta && meta.stil && !css.includes(`[data-stil="${meta.stil}"]`)) meldung(`${basis}/data/meta.json`, `stil ${meta.stil} kennt assets/handschrift.css nicht`);
  const manifest = json(`${basis}/data/manifest.json`);
  if (manifest) {
    if (!manifest.latestReport || !existsSync(join(ROOT, basis, manifest.latestReport))) {
      meldung(`${basis}/data/manifest.json`, "latestReport zeigt auf keine vorhandene Seite");
    }
    if (manifest.monitor && !existsSync(join(ROOT, basis, manifest.monitor))) {
      meldung(`${basis}/data/manifest.json`, `monitor ${manifest.monitor} fehlt`);
    }
  }

  const seiten = dateien(basis).filter((d) => d.endsWith(".html"));
  const anker = new Set(seiten.flatMap((s) => [...lesen(s).matchAll(/id="(q\d+)"/g)].map((m) => m[1])));
  for (const s of seiten) {
    for (const m of lesen(s).matchAll(/href="#(q\d+)"/g)) {
      if (!anker.has(m[1])) meldung(s, `Quellenverweis #${m[1]} ohne Eintrag unter Quellen`);
    }
  }

  // Figurenkanon: Gibt eine Seite ein Dossier wieder (data-kanon="lore/….md"), dann im Wortlaut des Spielers
  if (meta && meta.spielfigur && meta.spielfigur.kanon && !existsSync(join(ROOT, meta.spielfigur.kanon))) {
    meldung(`${basis}/data/meta.json`, `spielfigur.kanon ${meta.spielfigur.kanon} fehlt`);
  }
  for (const s of seiten) {
    const seite = lesen(s);
    const text = klartext(seite);
    for (const m of seite.matchAll(/data-kanon="([^"]*)"/g)) {
      if (!/^lore\/[a-z0-9-]+\.md$/.test(m[1]) || !existsSync(join(ROOT, m[1]))) {
        meldung(s, `data-kanon ${m[1]} gibt es nicht (erwartet lore/<name>.md)`);
        continue;
      }
      for (const absatz of kanonAbsaetze(lesen(m[1]))) {
        if (!text.includes(absatz)) meldung(s, `Figurenkanon weicht von ${m[1]} ab: „${absatz.slice(0, 50)} …“ steht nicht im Wortlaut auf der Seite`);
      }
    }
  }

  // Bücher (je Spielfigur eines) und Kapitel (fortlaufend über den ganzen Lauf)
  const chronikPfad = `${basis}/${(manifest && manifest.latestReport) || "chronik.html"}`;
  const chronik = existsSync(join(ROOT, chronikPfad)) ? lesen(chronikPfad) : "";
  for (const attr of ["farbe", "stil"]) {
    const gesetzt = (new RegExp(`<html[^>]*\\sdata-${attr}="([^"]*)"`).exec(chronik) || [])[1] || null;
    if (meta && (meta[attr] || null) !== gesetzt) meldung(chronikPfad, `data-${attr} ist ${gesetzt}, in meta.json steht ${meta[attr] || null}`);
  }
  const buecher = [...chronik.matchAll(/id="buch-(\d+)"/g)].map((m) => [Number(m[1]), m.index]);
  const kapitel = [...chronik.matchAll(/id="kapitel-(\d+)"/g)].map((m) => [Number(m[1]), m.index]);
  buecher.forEach(([nr], i) => { if (nr !== i + 1) meldung(chronikPfad, `Buch ${nr} an Stelle ${i + 1}: Bücher zählen ab 1 ohne Lücke`); });
  kapitel.forEach(([nr], i) => { if (nr !== i + 1) meldung(chronikPfad, `Kapitel ${nr} an Stelle ${i + 1}: Kapitel zählen über alle Bücher fortlaufend`); });
  if (kapitel.length && (!buecher.length || kapitel[0][1] < buecher[0][1])) meldung(chronikPfad, "Kapitel stehen in einem Buch (section id=\"buch-N\")");
  if (meta && Array.isArray(meta.buecher) && meta.buecher.length !== buecher.length) {
    meldung(`${basis}/data/meta.json`, `buecher nennt ${meta.buecher.length} Bücher, die Chronik hat ${buecher.length}`);
  }

  const ereignisse = json(`${basis}/data/events.json`);
  const eids = new Set();
  if (!Array.isArray(ereignisse)) meldung(`${basis}/data/events.json`, "muss eine Liste sein");
  for (const e of ereignisse || []) {
    const wo = `${basis}/data/events.json (${e.id})`;
    if (!new RegExp(`^${id}-\\d{4}$`).test(e.id || "")) meldung(wo, `id im Format ${id}-NNNN`);
    if (eids.has(e.id)) meldung(wo, "id doppelt");
    eids.add(e.id);
    if (!["fakt", "rekonstruktion"].includes(e.kind)) meldung(wo, "kind ist fakt (Belegt) oder rekonstruktion (Abgeleitet); Erzähltes gehört ins Tagebuch");
    for (const feld of ["category", "title", "description", "source"]) {
      if (typeof e[feld] !== "string" || !e[feld].trim()) meldung(wo, `Feld ${feld} fehlt`);
    }
    if (!TAG.test(e.recorded || "")) meldung(wo, "recorded (Tag der Aufnahme) im Format JJJJ-MM-TT");
    if (!spielzeitOk(e)) meldung(wo, "spieldatum (JJJJ-MM-TT) oder zeitraum ([von oder null, bis]) oder game_date_label nötig, nur eines davon");
    if (e.chapter !== undefined && !kapitel.some(([nr]) => nr === e.chapter)) meldung(wo, `chapter ${e.chapter} gibt es in der Chronik nicht`);
    for (const q of String(e.source || "").match(/Q\d+/g) || []) {
      if (!anker.has(q.toLowerCase())) meldung(wo, `Quelle ${q} steht unter Quellen der Chronik nicht`);
    }
    if (e.correction && (!TAG.test(e.correction.date || "") || !e.correction.note)) meldung(wo, "correction braucht date und note");
  }

  // Aufnahmen des Paradox-Monitors (von scripts/publish-monitor.py)
  const index = manifest && manifest.monitor ? json(`${basis}/${manifest.monitor}`) : null;
  if (index) {
    const ordner = dirname(`${basis}/${manifest.monitor}`);
    const wo = `${ordner}/index.json`;
    if (!WELT.test(index.world_id || "")) meldung(wo, `world_id ${index.world_id} unbekannten Formats`);
    if (meta && meta.monitor && meta.monitor.world_id !== index.world_id) meldung(`${basis}/data/meta.json`, "monitor.world_id passt nicht zu den Aufnahmen");
    const liste = Array.isArray(index.liste) ? index.liste : [];
    if (liste.length !== index.aufnahmen) meldung(wo, `aufnahmen ${index.aufnahmen}, in der Liste ${liste.length}`);
    for (const eintrag of liste) {
      const a = existsSync(join(ROOT, ordner, eintrag.aufnahme || "")) ? json(`${ordner}/${eintrag.aufnahme}`) : null;
      if (!a) {
        meldung(wo, `${eintrag.aufnahme} fehlt`);
        continue;
      }
      if (a.nr !== eintrag.nr || a.spieldatum !== eintrag.spieldatum || a.world_id !== index.world_id) {
        meldung(`${ordner}/${eintrag.aufnahme}`, "nr, spieldatum oder world_id passen nicht zu index.json");
      }
    }
    const bekannt = new Set(liste.map((e) => `${ordner}/${e.aufnahme}`));
    for (const d of dateien(`${ordner}/aufnahmen`)) {
      if (!bekannt.has(d)) meldung(d, "steht nicht in index.json (verworfene Aufnahmen bleiben draußen); publish-monitor.py erneut laufen lassen");
    }
    for (const [feld, schluessel, erwartet] of [["verlauf", "punkte", index.aufnahmen], ["chronik", "eintraege", index.chronik_eintraege]]) {
      const teil = index[feld] && existsSync(join(ROOT, ordner, index[feld])) ? json(`${ordner}/${index[feld]}`) : null;
      if (!teil) meldung(wo, `${feld} ${index[feld]} fehlt`);
      else if ((teil[schluessel] || []).length !== erwartet) meldung(`${ordner}/${index[feld]}`, `${(teil[schluessel] || []).length} ${schluessel}, laut index.json ${erwartet}`);
    }
  }
}

// 3. Monitor-Quellen gehören zu bekannten Läufen
for (const q of json("data/monitor-sources.json") || []) {
  const wo = `data/monitor-sources.json (${q.save})`;
  if (!ids.has(q.save)) meldung(wo, "Lauf steht nicht im Weltregister");
  if (q.world_id !== null && !WELT.test(q.world_id || "")) meldung(wo, `world_id ${q.world_id} unbekannten Formats (ck3:…)`);
  for (const feld of Object.keys(q.suche || {})) {
    if (!["angelegt_ab", "spielversion", "name", "start"].includes(feld)) meldung(wo, `suche.${feld} kennt publish-monitor.py nicht`);
  }
  if (q.suche && q.suche.angelegt_ab && !TAG.test(q.suche.angelegt_ab)) meldung(wo, "suche.angelegt_ab im Format JJJJ-MM-TT");
  if (q.abgeschlossen && !TAG.test(q.abgeschlossen.datum || "")) meldung(wo, "abgeschlossen.datum im Format JJJJ-MM-TT");
}

// 4. Schriften: lokal, mit Lizenztext und Prüfsumme; keine Anfragen an fremde Server
const alle = dateien("");
const quellen = existsSync(join(ROOT, "assets/fonts/QUELLEN.md")) ? lesen("assets/fonts/QUELLEN.md") : "";
if (!quellen) meldung("assets/fonts/QUELLEN.md", "fehlt (Herkunft und Lizenz der Schriften)");
for (const d of alle.filter((d) => /^assets\/fonts\/.+\.(woff2?|ttf|otf)$/.test(d))) {
  const summe = createHash("sha256").update(readFileSync(join(ROOT, d))).digest("hex");
  const name = d.split("/").pop();
  if (!new RegExp("`" + name.replace(/[.\-]/g, "\\$&") + "`[^\\n]*`" + summe + "`").test(quellen)) {
    meldung(d, "steht nicht mit dieser Prüfsumme in assets/fonts/QUELLEN.md (Schriften nur aus scripts/schriften.py)");
  }
}
const lizenzen = alle.filter((d) => /^assets\/fonts\/OFL-.+\.txt$/.test(d));
if (!lizenzen.length) meldung("assets/fonts", "Lizenztext der Schriften fehlt (OFL-*.txt)");
for (const d of lizenzen) {
  const text = lesen(d);
  if (!text.includes("SIL OPEN FONT LICENSE Version 1.1") || !/^Copyright /m.test(text)) meldung(d, "kein Text der SIL Open Font License 1.1 mit Urhebervermerk");
}
for (const m of css.matchAll(/url\(\s*["']?([^"')]+)["']?\s*\)/g)) {
  if (/^(https?:)?\/\//i.test(m[1]) || m[1].startsWith("data:")) meldung("assets/handschrift.css", `lädt ${m[1].slice(0, 50)}: nur lokale Dateien`);
  else if (!existsSync(join(ROOT, "assets", m[1]))) meldung("assets/handschrift.css", `${m[1]} fehlt`);
}
if (/@import/i.test(css)) meldung("assets/handschrift.css", "@import ist nicht erlaubt: nur lokale Dateien");
for (const d of alle.filter((d) => d.endsWith(".html"))) {
  const text = lesen(d);
  for (const m of text.matchAll(/<(script|img|iframe|source|audio|video|embed|object|link)\b[^>]*?\s(?:src|href|data)\s*=\s*["']([^"']+)["']/gi)) {
    const kanonisch = /rel\s*=\s*["']canonical["']/i.test(m[0]);
    if (/^(https?:)?\/\//i.test(m[2]) && !kanonisch) meldung(d, `lädt ${m[2].slice(0, 60)} von einem fremden Server`);
  }
  if (/url\(\s*["']?(https?:)?\/\//i.test(text) || /@import/i.test(text)) meldung(d, "lädt Stil oder Bild von einem fremden Server");
}

// 5. Datenschutz: Daten ohne Pfade, Konten und private Felder; im ganzen Repo keine Kontonummer und kein Spielstand
for (const d of alle.filter((d) => ROHDATEIEN.test(d))) meldung(d, "Rohdatei des Paradox-Monitors oder Spielstand: gehört nicht ins Repo");
for (const d of alle.filter((d) => d.endsWith(".json") && (d.startsWith("data/") || /^saves\/[^/]+\/data\//.test(d)))) {
  const text = lesen(d);
  const m = PRIVAT.exec(text);
  if (m) meldung(d, `enthält etwas wie einen Pfad, eine Kontokennung oder den Namen eines Spielstands („${m[0].slice(0, 40)}“)`);
  let inhalt = null;
  try { inhalt = JSON.parse(text); } catch { /* oben gemeldet oder keine Pflichtdatei */ }
  const schluessel = privateSchluessel(inhalt);
  if (schluessel.length) meldung(d, `enthält private Felder des Monitors: ${schluessel.slice(0, 4).join(", ")}`);
}
const MUSTERDATEIEN = new Set(["scripts/validate-data.mjs", "scripts/monitor_daten.py"]); // definieren die Muster selbst
for (const d of alle.filter((d) => /\.(json|html|md|js|mjs|py|css|txt|yml|svg|bat)$/.test(d) && !MUSTERDATEIEN.has(d))) {
  const m = KONTO.exec(lesen(d));
  if (m) meldung(d, `enthält einen Steam-Ordner mit Kontonummer, eine Kontokennung oder den Namen eines Spielstands („${m[0].slice(0, 40)}“)`);
}
for (const d of alle.filter((d) => /\.(webp|png|jpe?g|gif)$/i.test(d))) {
  const m = KONTO.exec(readFileSync(join(ROOT, d)).toString("latin1")) || /[A-Za-z]:\\(?:Users|Program Files)/.exec(readFileSync(join(ROOT, d)).toString("latin1"));
  if (m) meldung(d, `Bild enthält einen Pfad, eine Kontokennung oder den Namen eines Spielstands („${m[0].slice(0, 40)}“), etwa in den Metadaten`);
}

if (fehler.length) {
  console.error(`Datenprüfung: ${fehler.length} Fehler`);
  for (const f of fehler) console.error("  - " + f);
  process.exit(1);
}
console.log(`Datenprüfung ok: ${ids.size} ${ids.size === 1 ? "Lauf" : "Läufe"}, ${alle.length} Dateien geprüft.`);
