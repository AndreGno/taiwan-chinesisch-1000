import test from "node:test";
import assert from "node:assert/strict";
import { reviewCard, istFaellig } from "./srs.js";

test("erste korrekte Wiederholung setzt Intervall auf 1 Tag", () => {
  const karte = { interval: 0, repetitions: 0, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 2);
  assert.equal(ergebnis.interval, 1);
  assert.equal(ergebnis.repetitions, 1);
});

test("zweite korrekte Wiederholung setzt Intervall auf 6 Tage", () => {
  const karte = { interval: 1, repetitions: 1, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 2);
  assert.equal(ergebnis.interval, 6);
});

test("falsche Antwort setzt Wiederholungen zurück", () => {
  const karte = { interval: 10, repetitions: 3, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 0);
  assert.equal(ergebnis.repetitions, 0);
  assert.equal(ergebnis.interval, 1);
});

test("dueDate wird als lokales Datum berechnet, nicht ueber toISOString/UTC", () => {
  // 28.09.2026, 00:30 Uhr lokal + 1 Tag Intervall muss 2026-09-29 ergeben, nicht durch
  // eine UTC-Verschiebung auf 2026-09-28 zurueckfallen.
  const karte = { interval: 0, repetitions: 0, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 2, new Date(2026, 8, 28, 0, 30));
  assert.equal(ergebnis.dueDate, "2026-09-29");
});

test("istFaellig erkennt überfällige Karten", () => {
  assert.equal(istFaellig({ dueDate: "2020-01-01" }, "2026-01-01"), true);
  assert.equal(istFaellig({ dueDate: "2030-01-01" }, "2026-01-01"), false);
  assert.equal(istFaellig({}, "2026-01-01"), true);
});
