import test from "node:test";
import assert from "node:assert/strict";
import { quizVokabeln, quizOptionen } from "./vokabelquiz.js";

const vokabeln = [
  { zh: "你", pinyin: "nǐ", de: "du" },
  { zh: "我", pinyin: "wǒ", de: "ich" },
  { zh: "他", pinyin: "tā", de: "er" },
  { zh: "她", pinyin: "tā", de: "sie" },
  { zh: "您", pinyin: "nín", de: "du" }, // gleiche Bedeutung wie 你
];

test("quizVokabeln braucht Hanzi und Deutsch", () => {
  assert.equal(quizVokabeln([...vokabeln, { zh: "好", de: "" }, { zh: "", de: "gut" }]).length, 5);
});

test("quizOptionen: 4 verschiedene Antworten inkl. der richtigen", () => {
  for (let i = 0; i < 20; i++) {
    const optionen = quizOptionen(vokabeln[0], vokabeln, "de");
    assert.equal(optionen.length, 4);
    assert.ok(optionen.includes(vokabeln[0]));
    assert.equal(new Set(optionen.map((o) => o.de)).size, 4);
  }
});

test("quizOptionen: keine falsche Antwort mit gleicher Bedeutung wie die richtige", () => {
  for (let i = 0; i < 20; i++) {
    const optionen = quizOptionen(vokabeln[0], vokabeln, "de");
    assert.ok(!optionen.includes(vokabeln[4]));
  }
});

test("quizOptionen: bei zh-Antworten zählt das Hanzi, nicht die Bedeutung", () => {
  const optionen = quizOptionen(vokabeln[0], vokabeln, "zh");
  assert.equal(optionen.length, 4);
  assert.equal(new Set(optionen.map((o) => o.zh)).size, 4);
});
