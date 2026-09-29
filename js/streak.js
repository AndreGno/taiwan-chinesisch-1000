import { lokalesDatum, tageDifferenz } from "./datum.js";

const SPEICHER_SCHLUESSEL = "streak-status";

// Reine Funktion: kein Status → Streak 1. Gleicher Tag → unverändert. Gestern gelernt →
// +1. Lücke von 2 oder mehr Tagen (oder ein Status mit Datum in der Zukunft, was nur
// durch manuelle Manipulation vorkommen kann) → zurück auf 1.
export function berechneStreak(status, heute = lokalesDatum()) {
  if (!status || typeof status.letzterTag !== "string" || typeof status.streak !== "number") {
    return { letzterTag: heute, streak: 1 };
  }
  const differenz = tageDifferenz(status.letzterTag, heute);
  if (differenz === 0) return status;
  if (differenz === 1) return { letzterTag: heute, streak: status.streak + 1 };
  return { letzterTag: heute, streak: 1 };
}

function ladeStatus() {
  try {
    const wert = JSON.parse(localStorage.getItem(SPEICHER_SCHLUESSEL));
    return wert && typeof wert === "object" && !Array.isArray(wert) ? wert : null;
  } catch {
    return null;
  }
}

export function registriereLerntag() {
  const neuerStatus = berechneStreak(ladeStatus(), lokalesDatum());
  localStorage.setItem(SPEICHER_SCHLUESSEL, JSON.stringify(neuerStatus));
  return neuerStatus;
}

// Fuer das Badge: die Streak zaehlt nur, wenn der letzte Lerntag heute oder gestern war,
// sonst wird 0 angezeigt (auch wenn im Status noch eine hoehere Zahl steht).
export function aktuelleStreak(status = ladeStatus(), heute = lokalesDatum()) {
  if (!status || typeof status.letzterTag !== "string" || typeof status.streak !== "number") return 0;
  const differenz = tageDifferenz(status.letzterTag, heute);
  return differenz === 0 || differenz === 1 ? status.streak : 0;
}
