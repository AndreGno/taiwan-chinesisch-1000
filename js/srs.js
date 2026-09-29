import { lokalesDatum } from "./datum.js";

// Vereinfachtes SM-2, unveraendert aus dem Schwesterprojekt uebernommen — nur die
// Datumsberechnung wurde von toISOString() (UTC) auf das lokale Datum umgestellt.
export function reviewCard(karte, qualitaet, heute = new Date()) {
  let { interval, repetitions, easeFactor } = karte;
  if (qualitaet < 1) {
    repetitions = 0;
    interval = 1;
  } else {
    repetitions += 1;
    easeFactor = Math.max(
      1.3,
      easeFactor + (0.1 - (3 - qualitaet) * (0.08 + (3 - qualitaet) * 0.02))
    );
    if (repetitions === 1) interval = 1;
    else if (repetitions === 2) interval = 6;
    else interval = Math.round(interval * easeFactor);
  }
  const faellig = new Date(heute);
  faellig.setDate(faellig.getDate() + interval);
  return {
    ...karte,
    interval,
    repetitions,
    easeFactor,
    dueDate: lokalesDatum(faellig),
  };
}

export function istFaellig(karte, heute = lokalesDatum()) {
  return !karte.dueDate || karte.dueDate <= heute;
}
