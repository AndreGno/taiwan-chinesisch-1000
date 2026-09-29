import { lokalesDatum } from "./datum.js";

// Alle drei App-Schlüssel — beide Chinesisch-Apps laufen unter andregno.github.io, daher
// das zh1000-Präfix, damit sich Export/Import nicht mit dem Schwesterprojekt überschneiden.
const RELEVANTE_SCHLUESSEL = ["zh1000-fortschritt", "zh1000-karteikarten-status", "zh1000-streak-status"];

export function exportSchluessel() {
  return RELEVANTE_SCHLUESSEL;
}

export function exportiereFortschritt() {
  const daten = {};
  for (const schluessel of RELEVANTE_SCHLUESSEL) {
    const wert = localStorage.getItem(schluessel);
    if (wert) daten[schluessel] = JSON.parse(wert);
  }
  const blob = new Blob([JSON.stringify(daten, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `zh1000-fortschritt-${lokalesDatum()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function importiereFortschritt(datei) {
  const text = await datei.text();
  let daten;
  try {
    daten = JSON.parse(text);
  } catch {
    throw new Error("Die Datei enthält kein gültiges JSON.");
  }
  for (const schluessel of RELEVANTE_SCHLUESSEL) {
    if (daten[schluessel]) {
      localStorage.setItem(schluessel, JSON.stringify(daten[schluessel]));
    }
  }
}
