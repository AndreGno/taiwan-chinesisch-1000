import { ladeLektion, ladeFortschritt, markiereLektionBesucht, berechneLektionsFortschritt } from "./app.js";
import { verfuegbareTabs, rendereTabs, rendereTabInhalt } from "./lektion.js";
import { registriereLerntag, aktuelleStreak } from "./streak.js";

const titelEl = document.getElementById("lektion-titel");
const tabsEl = document.getElementById("tabs");
const inhaltEl = document.getElementById("tab-inhalt");
const streakBadge = document.getElementById("streak-badge");
const balkenEl = document.getElementById("lektion-fortschritt");
const keineStimmeHinweis = document.getElementById("keine-stimme-hinweis");

streakBadge.textContent = `🔥 ${aktuelleStreak()} Tage`;

const params = new URLSearchParams(location.search);
const nummer = Number(params.get("nr"));

async function start() {
  if (!Number.isInteger(nummer) || nummer <= 0) {
    titelEl.textContent = "Ungültige Lektion";
    inhaltEl.innerHTML = `<p class="fehler">Es wurde keine gültige Lektionsnummer (Parameter "nr") übergeben.</p>`;
    return;
  }

  let lektion;
  try {
    lektion = await ladeLektion(nummer);
  } catch (fehler) {
    titelEl.textContent = `Lektion ${nummer}`;
    inhaltEl.innerHTML = `<p class="fehler">${fehler.message}</p>`;
    return;
  }

  titelEl.textContent = `第${lektion.nummer}課 — ${lektion.titel_de || lektion.titel_zh || "Ohne Titel"}`;

  // Streak & Besucht-Markierung erst nach erfolgreichem Laden — ein 404 zählt nicht als
  // Lerntag.
  registriereLerntag();
  markiereLektionBesucht(lektion.nummer);
  streakBadge.textContent = `🔥 ${aktuelleStreak()} Tage`;

  function aktualisiereBalken() {
    const fortschritt = ladeFortschritt();
    const eintrag = fortschritt[`lektion-${lektion.nummer}`];
    const anteil = berechneLektionsFortschritt(lektion, eintrag);
    balkenEl.style.width = `${Math.round(anteil * 100)}%`;
  }

  const tabs = verfuegbareTabs(lektion);
  if (!tabs.length) {
    inhaltEl.innerHTML = `<p class="hinweis">Für diese Lektion liegen noch keine Inhalte vor.</p>`;
    aktualisiereBalken();
    return;
  }

  function zeige(tabKey) {
    markiereLektionBesucht(lektion.nummer, tabKey);
    rendereTabs(lektion, tabsEl, tabKey, zeige);
    rendereTabInhalt(lektion, tabKey, inhaltEl);
    aktualisiereBalken();
  }
  zeige(tabs[0].key);

  // Zusätzlicher Warnhinweis nur, wenn der Browser gar keine chinesische Stimme anbietet —
  // der permanente Hinweis auf "synthetische Sprachausgabe" steht unabhängig davon im HTML.
  const { chinesischeStimmeVerfuegbar } = await import("./tts.js");
  const verfuegbar = await chinesischeStimmeVerfuegbar();
  keineStimmeHinweis.hidden = verfuegbar;
}

start();
