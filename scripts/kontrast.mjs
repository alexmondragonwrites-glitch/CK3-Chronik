// CK3-Chronik · Kontrastprüfung nach WCAG 2 (AA) für assets/handschrift.css.
// Aufruf: node scripts/kontrast.mjs [--liste]
// Liest die Farbvariablen aus dem Stylesheet (hell und dunkel, je Farbe des Hauses) und prüft jede Paarung aus
// Schrift und Grund, die das Stylesheet verwendet: Lesetext mindestens 4,5 : 1, große Schrift (Initialen) 3 : 1.
// Die Pergamentwolken zählen mit: --hs-papier-fleck ist die ungünstigste Stelle der Kachel und wird hier aus der
// Kachel nachgerechnet.
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const css = readFileSync(join(ROOT, "assets", "handschrift.css"), "utf8");
const fehler = [];

// Schrift, Grund, Mindestkontrast
const PAARE = [
  ...["tinte", "tinte-blass", "rubrum", "gold-schrift", "haus"].flatMap((schrift) =>
    ["papier", "papier-fleck", "papier-2", "papier-3"].map((grund) => [schrift, grund, 4.5])),
  ["blau", "papier-3", 4.5],             // jedes zweite Absatzzeichen in Listen des Tagebuchs
  ["rubrum", "initiale-grund", 3],       // Schmuckinitialen: große Schrift
  ["blau", "initiale-grund", 3],
  ["einband-schrift", "einband", 4.5],   // Kopf und Fuß
  ["tinte", "initiale-grund", 4.5],
];

function hex(wert) {
  const m = /^#([0-9a-f]{6})$/i.exec(wert.trim());
  return m ? [0, 2, 4].map((i) => parseInt(m[1].slice(i, i + 2), 16)) : null;
}

function leuchtdichte([r, g, b]) {
  const k = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
  return 0.2126 * k(r) + 0.7152 * k(g) + 0.0722 * k(b);
}

function kontrast(a, b) {
  const [hell, dunkel] = [leuchtdichte(a), leuchtdichte(b)].sort((x, y) => y - x);
  return (hell + 0.05) / (dunkel + 0.05);
}

// Blöcke :root { … } und :root[data-farbe="x"] { … }, außerhalb und innerhalb von prefers-color-scheme: dark
const dunkelBereiche = [];
for (const m of css.matchAll(/@media\s*\(prefers-color-scheme:\s*dark\)\s*\{/g)) {
  let tiefe = 1;
  let i = m.index + m[0].length;
  for (; i < css.length && tiefe; i++) tiefe += css[i] === "{" ? 1 : css[i] === "}" ? -1 : 0;
  dunkelBereiche.push([m.index, i]);
}
const istDunkel = (ort) => dunkelBereiche.some(([a, b]) => ort > a && ort < b);
const bloecke = { hell: { "": {} }, dunkel: { "": {} } };
for (const m of css.matchAll(/:root(?:\[data-farbe="([a-z]+)"\])?\s*\{([^}]*)\}/g)) {
  const modus = istDunkel(m.index) ? "dunkel" : "hell";
  const ziel = (bloecke[modus][m[1] || ""] ||= {});
  for (const v of m[2].matchAll(/--hs-([a-z0-9-]+):\s*([^;]+);/g)) ziel[v[1]] = v[2].trim();
}
const farben = Object.keys(bloecke.hell).filter(Boolean);

function palette(modus, farbe) {
  return { ...bloecke.hell[""], ...(farbe ? bloecke.hell[farbe] : {}), ...(modus === "dunkel" ? { ...bloecke.dunkel[""], ...(farbe ? bloecke.dunkel[farbe] : {}) } : {}) };
}

// Ungünstigste Stelle des Pergaments aus der Kachel: Farbe der Wolken mal größte Deckkraft über der Papierfarbe
function fleck(modus) {
  const pfad = join(ROOT, "assets", `pergament-${modus}.png`);
  if (!existsSync(pfad)) return null;
  const daten = readFileSync(pfad);
  let farbe = null;
  let deckkraft = 0;
  for (let ort = 8; ort < daten.length;) {
    const laenge = daten.readUInt32BE(ort);
    const art = daten.toString("latin1", ort + 4, ort + 8);
    if (art === "PLTE") farbe = [daten[ort + 8], daten[ort + 9], daten[ort + 10]];
    if (art === "tRNS") deckkraft = Math.max(...daten.subarray(ort + 8, ort + 8 + laenge)) / 255;
    ort += 12 + laenge;
  }
  const papier = hex(palette(modus, "").papier);
  return farbe && papier ? papier.map((c, i) => Math.round(c * (1 - deckkraft) + farbe[i] * deckkraft)) : null;
}

for (const modus of ["hell", "dunkel"]) {
  const erwartet = fleck(modus);
  const gesetzt = hex(palette(modus, "")["papier-fleck"] || "");
  if (!erwartet) fehler.push(`assets/pergament-${modus}.png fehlt oder ist keine Kachel mit Farbtabelle`);
  else if (!gesetzt || erwartet.some((c, i) => Math.abs(c - gesetzt[i]) > 2)) {
    fehler.push(`--hs-papier-fleck (${modus}) ist ${palette(modus, "")["papier-fleck"]}, aus der Kachel ergibt sich #${erwartet.map((c) => c.toString(16).padStart(2, "0")).join("")}`);
  }
}

let geprueft = 0;
let knappster = [Infinity, ""];
const zeilen = [];
for (const modus of ["hell", "dunkel"]) {
  for (const farbe of ["", ...farben]) {
    const p = palette(modus, farbe);
    for (const [schrift, grund, mindestens] of PAARE) {
      const a = hex(p[schrift] || "");
      const b = hex(p[grund] || "");
      const wo = `${modus}${farbe ? `, ${farbe}` : ""}: ${schrift} auf ${grund}`;
      if (!a || !b) {
        fehler.push(`${wo}: Farbe fehlt oder ist kein #rrggbb`);
        continue;
      }
      const k = kontrast(a, b);
      geprueft += 1;
      zeilen.push(`${k.toFixed(2).padStart(6)}  (mind. ${mindestens})  ${wo}`);
      if (k < knappster[0]) knappster = [k, wo];
      if (k < mindestens) fehler.push(`${wo}: ${k.toFixed(2)} : 1, nötig ${mindestens} : 1`);
    }
  }
}

if (process.argv.includes("--liste")) console.log(zeilen.join("\n"));
if (fehler.length) {
  console.error(`Kontrastprüfung: ${fehler.length} Fehler`);
  for (const f of fehler) console.error("  - " + f);
  process.exit(1);
}
console.log(`Kontrast ok: ${geprueft} Paarungen in ${2 * (farben.length + 1)} Farbstellungen (hell und dunkel, ${farben.length + 1} Farben); am knappsten ${knappster[0].toFixed(2)} : 1 (${knappster[1]}).`);
