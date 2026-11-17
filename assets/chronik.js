// CK3-Chronik · Seite eines Laufs: Register aus data/events.json und Zeile zum Stand der Aufnahmen.
// Ohne Bibliotheken; die Seite bleibt ohne JavaScript lesbar.
(function () {
  "use strict";

  var ARTEN = { fakt: "Belegt", rekonstruktion: "Abgeleitet" };

  // Spieldatum „0875-02-13“ → „13.2.875“
  function spieldatum(text) {
    var t = /^(\d{1,4})-(\d{2})-(\d{2})$/.exec(text || "");
    return t ? Number(t[3]) + "." + Number(t[2]) + "." + Number(t[1]) : "–";
  }

  // Tag der Aufnahme „2026-11-17…“ → „17.11.2026“
  function tag(text) {
    var t = /^(\d{4})-(\d{2})-(\d{2})/.exec(text || "");
    return t ? Number(t[3]) + "." + Number(t[2]) + "." + t[1] : "–";
  }

  // Ein Eintrag hat ein eigenes Spieldatum oder den Zeitraum zwischen zwei Aufnahmen.
  function wann(e) {
    if (e.spieldatum) return spieldatum(e.spieldatum);
    var z = Array.isArray(e.zeitraum) ? e.zeitraum : [];
    if (z[0] && z[1] && z[0] !== z[1]) return "zwischen " + spieldatum(z[0]) + " und " + spieldatum(z[1]);
    if (z[1]) return spieldatum(z[1]);
    return e.game_date_label || "–";
  }

  function ordnung(e) {
    return e.spieldatum || (Array.isArray(e.zeitraum) && e.zeitraum[1]) || "";
  }

  function zahl(n) {
    return typeof n === "number" ? Math.round(n).toLocaleString("de-DE") : "–";
  }

  function zelle(zeile, text, klasse) {
    var td = document.createElement("td");
    if (klasse) td.className = klasse;
    td.textContent = text;
    zeile.appendChild(td);
    return td;
  }

  function quellenLinks(td, quelle) {
    td.textContent = "";
    String(quelle || "").split(/[,;]\s*/).forEach(function (q, i) {
      if (!q) return;
      if (i) td.appendChild(document.createTextNode(" "));
      if (/^Q\d+$/.test(q)) {
        var a = document.createElement("a");
        a.className = "hs-q";
        a.href = "#" + q.toLowerCase();
        a.textContent = q;
        td.appendChild(a);
      } else {
        td.appendChild(document.createTextNode(q));
      }
    });
  }

  function leerzeile(tbody, text) {
    var tr = document.createElement("tr");
    var td = zelle(tr, text, "hs-leer");
    td.colSpan = 5;
    tbody.textContent = "";
    tbody.appendChild(tr);
  }

  function register(eintraege) {
    var tbody = document.getElementById("register-zeilen");
    if (!tbody) return;
    var liste = eintraege.slice().sort(function (a, b) {
      return ordnung(a).localeCompare(ordnung(b)) || String(a.id).localeCompare(String(b.id));
    });
    if (!liste.length) {
      leerzeile(tbody, "Das Register füllt sich mit dem ersten Kapitel.");
      return;
    }
    tbody.textContent = "";
    liste.forEach(function (e) {
      var tr = document.createElement("tr");
      tr.id = e.id;
      zelle(tr, wann(e), "hs-zeit");
      zelle(tr, tag(e.recorded), "hs-zeit");
      zelle(tr, ARTEN[e.kind] || e.kind, "hs-art");
      var td = zelle(tr, "");
      var titel = document.createElement("strong");
      titel.textContent = e.title;
      td.appendChild(titel);
      if (e.description) td.appendChild(document.createTextNode(" " + e.description));
      if (e.correction) {
        var k = document.createElement("em");
        k.textContent = " Korrigiert am " + tag(e.correction.date) + ": " + e.correction.note;
        td.appendChild(k);
      }
      quellenLinks(zelle(tr, ""), e.source);
      tbody.appendChild(tr);
    });
  }

  function aufnahmen(index) {
    var p = document.getElementById("aufnahmen");
    if (!p || !index || !index.aufnahmen) return;
    p.textContent = "Aufnahmen des Paradox-Monitors: " + zahl(index.aufnahmen) + " bis zum Spieldatum " +
      spieldatum(index.spieldatum_bis) + ", zuletzt gespeichert am " + tag(index.gespeichert_bis) + ".";
  }

  function laden(pfad) {
    return fetch(pfad, { cache: "no-cache" }).then(function (r) {
      if (!r.ok) throw new Error(pfad + ": " + r.status);
      return r.json();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    laden("data/events.json").then(register).catch(function () {
      var tbody = document.getElementById("register-zeilen");
      if (tbody) leerzeile(tbody, "Das Register war gerade unerreichbar. Bitte die Seite neu laden.");
    });
    laden("data/manifest.json").then(function (manifest) {
      if (manifest && manifest.monitor) return laden(manifest.monitor).then(aufnahmen);
    }).catch(function () { /* Zeile bleibt beim Ausgangstext */ });
  });
})();
