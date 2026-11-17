// CK3-Chronik · neuen Lauf anlegen: Ordner, Seiten, Daten, Werkstatt und Einträge in den Registern.
// node scripts/new-save.mjs --id zweiter-lauf --name "Haus Beispiel" [--untertitel "Zweiter Lauf"]
//   [--started JJJJ-MM-TT] [--version "1.21"] [--farbe gruen] [--stil ranke]
// Die Weltkennung (playthrough_id) steht erst nach dem ersten Spielstand fest; bis dahin sucht
// scripts/publish-monitor.py die Welt über „suche“ in data/monitor-sources.json.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const FARBEN = ["blau", "rot", "gruen", "purpur", "schwarz", "gold"];   // wie in assets/handschrift.css
const STILE = ["ranke"];
const MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];

const args = Object.fromEntries(process.argv.slice(2).reduce((paare, a, i, alle) => {
  if (a.startsWith("--")) paare.push([a.slice(2), alle[i + 1] && !alle[i + 1].startsWith("--") ? alle[i + 1] : true]);
  return paare;
}, []));
const text = (wert) => (typeof wert === "string" ? wert : "");

const id = text(args.id);
const name = text(args.name);
const untertitel = text(args.untertitel);
const started = text(args.started) || new Date().toISOString().slice(0, 10);
const version = text(args.version);
const farbe = text(args.farbe);
const stil = text(args.stil);
if (!/^[a-z0-9-]+$/.test(id) || !name || !/^\d{4}-\d{2}-\d{2}$/.test(started)
    || (farbe && !FARBEN.includes(farbe)) || (stil && !STILE.includes(stil))) {
  console.error(`Aufruf: node scripts/new-save.mjs --id kennung --name "Name" [--untertitel "Zweiter Lauf"] [--started JJJJ-MM-TT] [--version "1.21"] [--farbe ${FARBEN.join("|")}] [--stil ${STILE.join("|")}]`);
  process.exit(2);
}
const basis = join(ROOT, "saves", id);
if (existsSync(basis)) {
  console.error(`saves/${id} gibt es schon.`);
  process.exit(3);
}

const json = (obj) => JSON.stringify(obj, null, 2) + "\n";
const schreiben = (pfad, inhalt) => {
  mkdirSync(dirname(pfad), { recursive: true });
  writeFileSync(pfad, inhalt, "utf8");
};
const html = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const [jahr, monat, tag] = started.split("-");
const beginn = `${Number(tag)}. ${MONATE[Number(monat) - 1]} ${jahr}`;
const titel = html(untertitel ? `${name} · ${untertitel}` : name);
const oben = `Crusader Kings III${untertitel ? ` · ${html(untertitel)}` : ""}`;
const wurzel = `<html lang="de"${farbe ? ` data-farbe="${farbe}"` : ""}${stil ? ` data-stil="${stil}"` : ""}>`;
const abschnitt = (kennung, nr, ueberschrift, inhalt) => `  <section class="hs-abschnitt" id="${kennung}" aria-labelledby="${kennung}-titel">
    <h2 id="${kennung}-titel"><span class="hs-nr">${nr}</span> ${ueberschrift}</h2>
    <div class="hs-leiste" aria-hidden="true"></div>
${inhalt}    <div class="hs-vierpass hs-schluss" aria-hidden="true"></div>
  </section>`;

schreiben(join(basis, "index.html"), `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${titel} · CK3-Chronik</title>
<link rel="icon" href="../../assets/zeichen.svg" type="image/svg+xml">
<meta http-equiv="refresh" content="0; url=chronik.html">
<link rel="canonical" href="chronik.html">
</head>
<body><p><a href="chronik.html">Zur Chronik „${titel}“</a></p></body>
</html>
`);

schreiben(join(basis, "chronik.html"), `<!doctype html>
${wurzel}
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>${titel} · CK3-Chronik</title>
<meta name="description" content="Hauschronik einer Partie in Crusader Kings III, erzählt im Tagebuch der Spielfigur, mit Aufnahmen aus den Spielständen.">
<link rel="icon" href="../../assets/zeichen.svg" type="image/svg+xml">
<link rel="stylesheet" href="../../assets/handschrift.css">
<script src="../../assets/chronik.js" defer></script>
</head>
<body>
<a class="hs-sprung" href="#inhalt">Zum Inhalt</a>
<header class="hs-kopf">
  <div class="hs-kopf-innen">
    <a class="hs-marke" href="../../">CK3-Chronik</a>
    <nav aria-label="Abschnitte">
      <a href="#steckbrief">Steckbrief</a>
      <a href="#register">Register</a>
      <a href="#buecher">Bücher</a>
      <a href="#haus">Haus</a>
      <a href="#quellen">Quellen</a>
    </nav>
  </div>
  <div class="hs-leiste" aria-hidden="true"></div>
</header>

<main id="inhalt" data-lauf="${id}">
  <section class="hs-titelblatt" aria-labelledby="titel">
    <p class="hs-oben">${oben}</p>
    <div class="hs-vierpass" aria-hidden="true"></div>
    <h1 id="titel">${html(name)}</h1>
    <p class="hs-unter">Eine Hauschronik, erzählt im Tagebuch der Spielfigur</p>
    <p class="hs-zeile">Begonnen am ${beginn}${version ? ` · Version ${html(version)}` : ""}</p>
  </section>

  <p class="hs-hinweis">Spielfigur, Haus und Startjahr trägt die Chronik ein, sobald der erste Spielstand der Partie gelesen ist.</p>
  <p class="hs-aufnahmen" id="aufnahmen" aria-live="polite">Die Aufnahmen beginnen mit dem ersten Spielstand der Partie.</p>

  <nav class="hs-inhalt" aria-labelledby="inhalt-titel">
    <h2 id="inhalt-titel">Inhalt</h2>
    <ol>
      <li><a href="#steckbrief"><span class="hs-nr">I</span> Steckbrief der Partie</a></li>
      <li><a href="#register"><span class="hs-nr">II</span> Register</a></li>
      <li><a href="#buecher"><span class="hs-nr">III</span> Bücher und Kapitel</a></li>
      <li><a href="#haus"><span class="hs-nr">IV</span> Haus und Titel</a></li>
      <li><a href="#fragen"><span class="hs-nr">V</span> Offene Fragen</a></li>
      <li><a href="#quellen"><span class="hs-nr">VI</span> Quellen</a></li>
      <li><a href="#korrekturen"><span class="hs-nr">VII</span> Korrekturen</a></li>
    </ol>
  </nav>

${abschnitt("steckbrief", "I", "Steckbrief der Partie", `    <div class="hs-bericht">
      <span class="hs-etikett">Belegt</span>
      <dl class="hs-steckbrief">
        <dt>Spiel</dt><dd>Crusader Kings III${version ? `, Version ${html(version)}` : ""}</dd>
        <dt>Begonnen</dt><dd>${beginn}</dd>
        <dt>Spielfigur</dt><dd>folgt mit dem ersten Spielstand</dd>
        <dt>Haus</dt><dd>folgt mit dem ersten Spielstand</dd>
        <dt>Startjahr</dt><dd>folgt mit dem ersten Spielstand</dd>
        <dt>Erzählweise</dt><dd>Tagebuch der Spielfigur; je Spielfigur ein Buch, die Kapitel zählen über den ganzen Lauf.</dd>
      </dl>
    </div>
`)}

${abschnitt("register", "II", "Register", `    <p class="hs-hinweis">Das Register nennt, was die Spielstände belegen und was daraus abgeleitet ist. Ein Eintrag trägt sein Spieldatum oder den Zeitraum zwischen zwei Aufnahmen, daneben steht der Tag der Aufnahme.</p>
    <div class="hs-tabelle-rahmen"><table class="hs-register">
      <thead><tr><th scope="col">Spieldatum</th><th scope="col">Aufnahme</th><th scope="col">Art</th><th scope="col">Ereignis</th><th scope="col">Quelle</th></tr></thead>
      <tbody id="register-zeilen"><tr><td class="hs-leer" colspan="5">Das Register lädt …</td></tr></tbody>
    </table></div>
`)}

${abschnitt("buecher", "III", "Bücher und Kapitel", `    <!-- Je Spielfigur ein Buch: <section class="hs-buch" id="buch-N">, darin die Kapitel als
         <article class="hs-kapitel" id="kapitel-N">. Kapitel zählen über alle Bücher fortlaufend (docs/, Regeln des Laufs). -->
    <p class="hs-leer">Das erste Buch beginnt mit der ersten Spielfigur. Kapitel I entsteht nach dem ersten Einschnitt der Partie.</p>
`)}

${abschnitt("haus", "IV", "Haus und Titel", `    <p class="hs-leer">Haus, Dynastie und Titel folgen mit dem ersten Spielstand.</p>
`)}

${abschnitt("fragen", "V", "Offene Fragen", `    <ul>
      <li>Wer ist die erste Spielfigur, welches Haus führt sie und in welchem Jahr beginnt die Partie? Das zeigt der erste Spielstand.</li>
    </ul>
`)}

${abschnitt("quellen", "VI", "Quellen", `    <ol class="hs-quellen"></ol>
`)}

${abschnitt("korrekturen", "VII", "Korrekturen", `    <p class="hs-leer">Noch keine.</p>
`)}
</main>

<footer class="hs-fuss">
  <div class="hs-leiste" aria-hidden="true"></div>
  <div class="hs-fuss-innen">
    <p><a href="../../">CK3-Chronik</a> · Chroniken eigener Partien in Crusader Kings III.</p>
    <p>Eine private Fan-Chronik, unabhängig von Paradox Interactive. Crusader Kings ist eine Marke von Paradox Interactive AB.</p>
  </div>
</footer>
</body>
</html>
`);

schreiben(join(basis, "data", "meta.json"), json({
  id, name, ...(untertitel ? { lauf: untertitel } : {}), name_status: "Arbeitstitel", game: "Crusader Kings III",
  ...(version ? { game_version: version } : {}), status: "laufend", started,
  ...(farbe ? { farbe } : {}), ...(stil ? { stil } : {}),
  buecher: [],
  monitor: { world_id: null },
}));
schreiben(join(basis, "data", "manifest.json"), json({ latestReport: "chronik.html", monitor: null }));
schreiben(join(basis, "data", "events.json"), "[]\n");
const laufname = untertitel ? `${name} · ${untertitel}` : name;
schreiben(join(ROOT, "werkstatt", id, "STAND.md"), `# ${laufname} · Stand\n\nAngelegt am ${started}. Noch kein Buch und kein Kapitel; nächste freie Quellennummer: Q1.\n`);
schreiben(join(ROOT, "werkstatt", id, "fakten", "LIESMICH.md"), `# Faktenblätter\n\nJe Kapitel ein Faktenblatt \`kapitel-N.md\` aus den Aufnahmen des Paradox-Monitors für den Zeitraum des Kapitels. Erzeugt von \`scripts/fakten.py\` (\`--save ${id} --kapitel N --bis JJJJ-MM-TT\`), nicht von Hand ändern.\n\nWas die Aufnahmen nicht hergeben (Angaben des Spielers, Funde aus dem Spielstand, Texte des Spiels), steht von Hand im Beiblatt \`kapitel-N-beiblatt.md\`; das Skript hängt es an das Faktenblatt an.\n`);
schreiben(join(ROOT, "werkstatt", id, "figuren", "LIESMICH.md"), `# Figurenprofile\n\nJe Erbe ein Profil aus dem Spielstand (Eigenschaften, Erziehung, Fertigkeiten, Familie, Glaube, Erinnerungen). Was der Spieler ergänzt, wandert nach \`lore/\` und gilt dann als Kanon.\n`);

const weltenPfad = join(ROOT, "data", "worlds.json");
const welten = JSON.parse(readFileSync(weltenPfad, "utf8"));
welten.push({ id, name, ...(untertitel ? { untertitel } : {}), path: `saves/${id}/`, page: "chronik.html", status: "laufend", started, description: "" });
writeFileSync(weltenPfad, json(welten), "utf8");
// Karte im Portal: Sie bleibt ohne JavaScript stehen; mit JavaScript baut assets/portal.js die Karten aus dem Weltregister.
const portalPfad = join(ROOT, "index.html");
const MARKE = "      <!-- NEUER LAUF:";
const portal = readFileSync(portalPfad, "utf8");
if (portal.includes(MARKE)) {
  const karte = `      <a class="hs-welt" href="saves/${id}/chronik.html">
        <span class="hs-status">${untertitel ? `${html(untertitel)} · seit` : "läuft seit"} ${Number(tag)}.${Number(monat)}.${jahr}</span>
        <h3>${html(name)}</h3>
        <p></p>
        <p class="hs-mehr">Zur Chronik</p>
      </a>
`;
  writeFileSync(portalPfad, portal.replace(MARKE, karte + MARKE), "utf8");
} else {
  console.error("index.html: Marke „NEUER LAUF“ fehlt, die Karte des Laufs bitte von Hand eintragen.");
}
const quellenPfad = join(ROOT, "data", "monitor-sources.json");
const quellen = JSON.parse(readFileSync(quellenPfad, "utf8"));
quellen.push({ save: id, name: untertitel || name, world_id: null, suche: { angelegt_ab: started, ...(version ? { spielversion: version.split(" ")[0] } : {}) } });
writeFileSync(quellenPfad, json(quellen), "utf8");
console.log(`Angelegt: saves/${id}/ und werkstatt/${id}/, eingetragen in data/worlds.json, data/monitor-sources.json und index.html.`);
