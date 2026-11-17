// CK3-Chronik · Musterblatt: Farbe des Hauses umschalten (data-farbe an <html>), auch über ?farbe=gruen.
(function () {
  "use strict";

  var FARBEN = ["", "rot", "gruen", "purpur", "schwarz", "gold"];

  function setzen(farbe) {
    if (FARBEN.indexOf(farbe) < 0) farbe = "";
    if (farbe) document.documentElement.setAttribute("data-farbe", farbe);
    else document.documentElement.removeAttribute("data-farbe");
    document.querySelectorAll("#farbwahl button").forEach(function (knopf) {
      knopf.setAttribute("aria-pressed", String(knopf.getAttribute("data-farbe") === farbe));
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var wahl = document.getElementById("farbwahl");
    if (!wahl) return;
    wahl.hidden = false;
    wahl.addEventListener("click", function (ereignis) {
      var knopf = ereignis.target.closest("button[data-farbe]");
      if (knopf) setzen(knopf.getAttribute("data-farbe"));
    });
    setzen(new URLSearchParams(location.search).get("farbe") || "");
  });
})();
