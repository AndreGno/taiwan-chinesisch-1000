import test from "node:test";
import assert from "node:assert/strict";
import { berechneStreak, aktuelleStreak } from "./streak.js";

test("kein Status ergibt Streak 1", () => {
  const ergebnis = berechneStreak(null, "2026-09-28");
  assert.deepEqual(ergebnis, { letzterTag: "2026-09-28", streak: 1 });
});

test("ein fehlerhafter/unvollständiger Status wird wie kein Status behandelt", () => {
  const ergebnis = berechneStreak({ irgendwas: true }, "2026-09-28");
  assert.deepEqual(ergebnis, { letzterTag: "2026-09-28", streak: 1 });
});

test("gleicher Tag bleibt unverändert", () => {
  const status = { letzterTag: "2026-09-28", streak: 4 };
  const ergebnis = berechneStreak(status, "2026-09-28");
  assert.deepEqual(ergebnis, status);
});

test("gestern gelernt erhöht die Streak um 1", () => {
  const status = { letzterTag: "2026-09-27", streak: 4 };
  const ergebnis = berechneStreak(status, "2026-09-28");
  assert.deepEqual(ergebnis, { letzterTag: "2026-09-28", streak: 5 });
});

test("eine Lücke von 2 oder mehr Tagen setzt die Streak auf 1 zurück", () => {
  const status = { letzterTag: "2026-09-20", streak: 10 };
  const ergebnis = berechneStreak(status, "2026-09-28");
  assert.deepEqual(ergebnis, { letzterTag: "2026-09-28", streak: 1 });
});

test("ein letzterTag in der Zukunft wird wie eine Luecke behandelt", () => {
  const status = { letzterTag: "2026-10-05", streak: 10 };
  const ergebnis = berechneStreak(status, "2026-09-28");
  assert.deepEqual(ergebnis, { letzterTag: "2026-09-28", streak: 1 });
});

test("aktuelleStreak zeigt 0, wenn der letzte Lerntag länger als gestern her ist", () => {
  assert.equal(aktuelleStreak({ letzterTag: "2026-09-20", streak: 7 }, "2026-09-28"), 0);
});

test("aktuelleStreak zeigt die Streak, wenn heute oder gestern gelernt wurde", () => {
  assert.equal(aktuelleStreak({ letzterTag: "2026-09-28", streak: 7 }, "2026-09-28"), 7);
  assert.equal(aktuelleStreak({ letzterTag: "2026-09-27", streak: 7 }, "2026-09-28"), 7);
});

test("aktuelleStreak liefert 0 ohne Status", () => {
  assert.equal(aktuelleStreak(null, "2026-09-28"), 0);
});
