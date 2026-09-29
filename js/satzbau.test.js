import test from "node:test";
import assert from "node:assert/strict";
import { mische, zerlegeInZeichen, pruefeSatz } from "./satzbau.js";

test("zerlegeInZeichen entfernt Satzzeichen und zerlegt in Einzelzeichen", () => {
  assert.deepEqual(zerlegeInZeichen("你好，嗎？"), ["你", "好", "嗎"]);
});

test("zerlegeInZeichen liefert [] für leer/undefined", () => {
  assert.deepEqual(zerlegeInZeichen(""), []);
  assert.deepEqual(zerlegeInZeichen(undefined), []);
});

test("pruefeSatz erkennt korrekte und falsche Reihenfolge", () => {
  assert.equal(pruefeSatz("你好嗎", "你好，嗎？"), true);
  assert.equal(pruefeSatz("嗎你好", "你好，嗎？"), false);
});

test("mische liefert eine Permutation und verändert das Original nicht", () => {
  const original = ["你", "好", "嗎", "呢"];
  const kopie = [...original];
  const gemischt = mische(original);
  assert.deepEqual(original, kopie);
  assert.equal(gemischt.length, original.length);
  assert.deepEqual([...gemischt].sort(), [...original].sort());
});
