import test from "node:test";
import assert from "node:assert/strict";
import { faelligeVokabeln } from "./karteikarten.js";

test("faelligeVokabeln: ohne Status ist alles mit zh faellig", () => {
  const vokabeln = [{ zh: "你" }, { zh: "好" }, { pinyin: "ohne zh" }];
  assert.deepEqual(faelligeVokabeln(vokabeln, {}, "2026-09-28"), [{ zh: "你" }, { zh: "好" }]);
});

test("faelligeVokabeln: Karten mit zukünftigem dueDate sind nicht faellig", () => {
  const vokabeln = [{ zh: "你" }, { zh: "好" }];
  const status = { 你: { dueDate: "2030-01-01" }, 好: { dueDate: "2020-01-01" } };
  assert.deepEqual(faelligeVokabeln(vokabeln, status, "2026-09-28"), [{ zh: "好" }]);
});
