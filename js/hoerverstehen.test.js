import test from "node:test";
import assert from "node:assert/strict";
import { mische, erzeugeOptionen } from "./hoerverstehen.js";

test("mische liefert eine Permutation und verändert das Original nicht", () => {
  const original = [1, 2, 3, 4, 5];
  const kopie = [...original];
  const gemischt = mische(original);
  assert.deepEqual(original, kopie);
  assert.deepEqual([...gemischt].sort(), [...original].sort());
});

test("erzeugeOptionen enthält immer die Zielzeile und ist eindeutig", () => {
  const zeilen = [{ de: "a" }, { de: "b" }, { de: "c" }, { de: "d" }, { de: "e" }];
  const optionen = erzeugeOptionen(zeilen[0], zeilen, 4);
  assert.equal(optionen.length, 4);
  assert.ok(optionen.includes(zeilen[0]));
  assert.equal(new Set(optionen).size, 4);
});

test("erzeugeOptionen kappt bei weniger verfügbaren Zeilen als angefragt", () => {
  const zeilen = [{ de: "a" }, { de: "b" }];
  const optionen = erzeugeOptionen(zeilen[0], zeilen, 4);
  assert.equal(optionen.length, 2);
});
