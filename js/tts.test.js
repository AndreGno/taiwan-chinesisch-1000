import test from "node:test";
import assert from "node:assert/strict";
import { waehleStimme } from "./tts.js";

test("waehleStimme bevorzugt exakt zh-TW", () => {
  const stimmen = [{ lang: "en-US" }, { lang: "zh-CN" }, { lang: "zh-TW" }];
  assert.equal(waehleStimme(stimmen).lang, "zh-TW");
});

test("waehleStimme akzeptiert Unterstrich-Schreibweise (Android)", () => {
  const stimmen = [{ lang: "en-US" }, { lang: "zh_TW" }];
  assert.equal(waehleStimme(stimmen).lang, "zh_TW");
});

test("waehleStimme fällt auf zh-Hant zurück, wenn kein zh-TW vorhanden ist", () => {
  const stimmen = [{ lang: "en-US" }, { lang: "zh-Hant" }];
  assert.equal(waehleStimme(stimmen).lang, "zh-Hant");
});

test("waehleStimme fällt auf irgendeine zh/cmn-Stimme zurück", () => {
  const stimmen = [{ lang: "en-US" }, { lang: "cmn-Hans-CN" }];
  assert.equal(waehleStimme(stimmen).lang, "cmn-Hans-CN");
});

test("waehleStimme liefert null ohne chinesische Stimme", () => {
  assert.equal(waehleStimme([{ lang: "en-US" }, { lang: "de-DE" }]), null);
  assert.equal(waehleStimme([]), null);
});
