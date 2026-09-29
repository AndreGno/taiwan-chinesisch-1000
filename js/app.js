const FORTSCHRITT_SCHLUESSEL = "zh1000-fortschritt";

// Ersetzt die für innerHTML riskanten Zeichen. Die Lektionsdaten stammen aus einer
// automatischen PDF-Extraktion (siehe docs/superpowers/specs) — ein Parserfehler könnte
// ein "<" oder "&" ins JSON schreiben, das sonst als Markup interpretiert würde.
export function escapeHtml(text) {
  return String(text ?? "").replace(/[&<>"']/g, (zeichen) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[zeichen]);
}

// Füllt fehlende/leere Felder mit "" bzw. [] — die Design-Spec erlaubt ausdrücklich, dass
// jedes Feld leer sein darf, solange der Parser noch nicht alle 75 Lektionen liefert.
export function normalisiereLektion(lektion) {
  return {
    nummer: lektion?.nummer ?? 0,
    titel_zh: lektion?.titel_zh ?? "",
    titel_de: lektion?.titel_de ?? "",
    dialog: Array.isArray(lektion?.dialog) ? lektion.dialog : [],
    vokabeln: Array.isArray(lektion?.vokabeln) ? lektion.vokabeln : [],
    grammatik: Array.isArray(lektion?.grammatik) ? lektion.grammatik : [],
  };
}

export async function ladeLektionsListe() {
  let antwort;
  try {
    antwort = await fetch("data/lektionen.json");
  } catch {
    throw new Error("Lektionsliste konnte nicht geladen werden (keine Verbindung).");
  }
  if (!antwort.ok) throw new Error("Lektionsliste (data/lektionen.json) wurde nicht gefunden.");
  return antwort.json();
}

export async function ladeLektion(nummer) {
  const id = String(nummer).padStart(2, "0");
  let antwort;
  try {
    antwort = await fetch(`data/lektion-${id}.json`);
  } catch {
    throw new Error(`Lektion ${nummer} konnte nicht geladen werden (keine Verbindung).`);
  }
  if (!antwort.ok) throw new Error(`Lektion ${nummer} wurde nicht gefunden.`);
  const daten = await antwort.json();
  return normalisiereLektion(daten);
}

export function ladeFortschritt() {
  try {
    const wert = JSON.parse(localStorage.getItem(FORTSCHRITT_SCHLUESSEL) || "{}");
    return wert && typeof wert === "object" && !Array.isArray(wert) ? wert : {};
  } catch {
    return {};
  }
}

export function speichereFortschritt(fortschritt) {
  localStorage.setItem(FORTSCHRITT_SCHLUESSEL, JSON.stringify(fortschritt));
}

// Die Inhalts-Tabs einer Lektion (ohne "Übungen", das ist ein Aktionsbereich, kein
// Lerninhalt) — nur die mit tatsächlichen Daten zählen für den Fortschritt.
export function verfuegbareInhaltsTabs(lektion) {
  const tabs = [];
  if (lektion.dialog.length) tabs.push("dialog");
  if (lektion.vokabeln.length) tabs.push("vokabeln");
  if (lektion.grammatik.length) tabs.push("grammatik");
  return tabs;
}

// Markiert eine Lektion als besucht (für den Startseiten-Fortschritt) und optional einen
// konkret geöffneten Tab (für den Fortschrittsbalken auf der Lektionsseite).
export function markiereLektionBesucht(nummer, tabKey) {
  const fortschritt = ladeFortschritt();
  const schluessel = `lektion-${nummer}`;
  const eintrag = fortschritt[schluessel] ?? { besucht: false, tabsBesucht: [] };
  eintrag.besucht = true;
  if (tabKey && !eintrag.tabsBesucht.includes(tabKey)) eintrag.tabsBesucht.push(tabKey);
  fortschritt[schluessel] = eintrag;
  speichereFortschritt(fortschritt);
  return fortschritt;
}

// Fortschritt einer einzelnen Lektion: besuchte Inhalts-Tabs / vorhandene Inhalts-Tabs.
// Ohne jeden Inhalt (alle Felder leer) zählt allein der Besuch der Lektionsseite.
export function berechneLektionsFortschritt(lektion, eintrag) {
  const inhaltsTabs = verfuegbareInhaltsTabs(lektion);
  if (inhaltsTabs.length === 0) return eintrag?.besucht ? 1 : 0;
  const besuchte = (eintrag?.tabsBesucht ?? []).filter((tab) => inhaltsTabs.includes(tab));
  return besuchte.length / inhaltsTabs.length;
}

// Gesamt-Fortschritt auf der Startseite: besuchte Lektionen / Anzahl in lektionen.json.
export function berechneGesamtFortschritt(lektionen, fortschritt) {
  if (!lektionen.length) return 0;
  const besucht = lektionen.filter((l) => fortschritt[`lektion-${l.nummer}`]?.besucht).length;
  return besucht / lektionen.length;
}

// Grid auf der Startseite kennt nur nummer/titel_zh/titel_de (aus lektionen.json) — der
// Fortschrittsbalken pro Karte zeigt daher nur besucht/nicht besucht, keine Tab-Details
// (die bräuchten den vollen Lektions-Datensatz, den wir hier bewusst nicht nachladen).
export function rendereLektionsGrid(lektionen, fortschritt, container) {
  container.innerHTML = "";
  if (!lektionen.length) {
    container.innerHTML = `<p class="hinweis">Noch keine Lektionen vorhanden.</p>`;
    return;
  }
  for (const lektion of lektionen) {
    const besucht = Boolean(fortschritt[`lektion-${lektion.nummer}`]?.besucht);
    const a = document.createElement("a");
    a.href = `lektion.html?nr=${lektion.nummer}`;
    a.className = besucht ? "lektion-karte besucht" : "lektion-karte";
    a.innerHTML = `
      <p class="zh">第${lektion.nummer}課 ${escapeHtml(lektion.titel_zh)}</p>
      <p class="de">${escapeHtml(lektion.titel_de)}</p>
      <div class="fortschritt-balken"><span style="width:${besucht ? 100 : 0}%"></span></div>
    `;
    container.appendChild(a);
  }
}
