import test from "node:test";
import assert from "node:assert/strict";
import { lokalesDatum, tageDifferenz } from "./datum.js";

test("lokalesDatum nutzt lokale Getter statt UTC", () => {
  // 28.09.2026, 00:30 Uhr lokal — mit toISOString() würde das (je nach Zeitzone
  // westlich von UTC) noch als 27.09. erscheinen.
  assert.equal(lokalesDatum(new Date(2026, 8, 28, 0, 30)), "2026-09-28");
});

test("tageDifferenz über einen Jahreswechsel", () => {
  assert.equal(tageDifferenz("2026-12-31", "2027-01-01"), 1);
});

test("tageDifferenz über einen Schalttag", () => {
  assert.equal(tageDifferenz("2028-02-28", "2028-02-29"), 1);
});

test("tageDifferenz über eine Sommerzeit-Umstellung (Europa, Ende Oktober)", () => {
  assert.equal(tageDifferenz("2026-10-24", "2026-10-26"), 2);
});

test("tageDifferenz ist negativ, wenn datumB vor datumA liegt", () => {
  assert.equal(tageDifferenz("2026-09-28", "2026-09-20"), -8);
});
