import test from "node:test";
import assert from "node:assert/strict";
import { bewerteAussprache } from "./aussprache.js";

test("bewerteAussprache: identischer Text ergibt 'Sehr gut!'", () => {
  assert.equal(bewerteAussprache("你好嗎", "你好嗎").label, "Sehr gut!");
});

test("bewerteAussprache ignoriert Interpunktion auf beiden Seiten", () => {
  const bewertung = bewerteAussprache("你好嗎", "你好嗎？");
  assert.equal(bewertung.label, "Sehr gut!");
  assert.equal(bewertung.score, 1);
});

test("bewerteAussprache: völlig anderer Text ergibt 'Nochmal versuchen.'", () => {
  assert.equal(bewerteAussprache("再見", "你好嗎").label, "Nochmal versuchen.");
});
