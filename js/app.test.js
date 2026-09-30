import test from "node:test";
import assert from "node:assert/strict";
import {
  escapeHtml,
  normalisiereLektion,
  verfuegbareInhaltsTabs,
  berechneLektionsFortschritt,
  berechneGesamtFortschritt,
} from "./app.js";

test("escapeHtml ersetzt gefährliche Zeichen", () => {
  assert.equal(escapeHtml(`<b>"Test" & 'Sache'</b>`), "&lt;b&gt;&quot;Test&quot; &amp; &#39;Sache&#39;&lt;/b&gt;");
  assert.equal(escapeHtml(undefined), "");
});

test("normalisiereLektion füllt fehlende Felder", () => {
  const ergebnis = normalisiereLektion({ nummer: 5, titel_zh: "測試" });
  assert.deepEqual(ergebnis, {
    nummer: 5,
    titel_zh: "測試",
    titel_de: "",
    dialog: [],
    vokabeln: [],
    grammatik: [],
    sprichwort: null,
  });
});

test("normalisiereLektion übernimmt ein Sprichwort, sonst null", () => {
  const sprichwort = { zh: "名師出高徒", pinyin: "Míngshī chū gāotú", de: "Ein großer Meister …" };
  assert.deepEqual(normalisiereLektion({ nummer: 40, sprichwort }).sprichwort, sprichwort);
  assert.equal(normalisiereLektion({ nummer: 1, sprichwort: null }).sprichwort, null);
});

test("normalisiereLektion übernimmt vorhandene Arrays unverändert", () => {
  const lektion = { nummer: 1, dialog: [{ zh: "你好" }], vokabeln: [], grammatik: [] };
  assert.deepEqual(normalisiereLektion(lektion).dialog, [{ zh: "你好" }]);
});

test("verfuegbareInhaltsTabs listet nur Tabs mit Inhalt", () => {
  const leer = normalisiereLektion({ nummer: 1 });
  assert.deepEqual(verfuegbareInhaltsTabs(leer), []);
  const voll = normalisiereLektion({
    nummer: 1,
    dialog: [{ zh: "你好" }],
    vokabeln: [],
    grammatik: [{ titel: "x" }],
  });
  assert.deepEqual(verfuegbareInhaltsTabs(voll), ["dialog", "grammatik"]);
});

test("berechneLektionsFortschritt: ohne Inhalt zählt nur der Besuch", () => {
  const leer = normalisiereLektion({ nummer: 1 });
  assert.equal(berechneLektionsFortschritt(leer, undefined), 0);
  assert.equal(berechneLektionsFortschritt(leer, { besucht: true, tabsBesucht: [] }), 1);
});

test("berechneLektionsFortschritt: Anteil besuchter Inhalts-Tabs", () => {
  const lektion = normalisiereLektion({
    nummer: 1,
    dialog: [{ zh: "你好" }],
    vokabeln: [{ zh: "你" }],
    grammatik: [],
  });
  const eintrag = { besucht: true, tabsBesucht: ["dialog"] };
  assert.equal(berechneLektionsFortschritt(lektion, eintrag), 0.5);
});

test("berechneGesamtFortschritt: 0 ohne Lektionen", () => {
  assert.equal(berechneGesamtFortschritt([], {}), 0);
});

test("berechneGesamtFortschritt: Anteil besuchter Lektionen", () => {
  const lektionen = [{ nummer: 1 }, { nummer: 2 }, { nummer: 3 }, { nummer: 4 }];
  const fortschritt = { "lektion-1": { besucht: true }, "lektion-3": { besucht: true } };
  assert.equal(berechneGesamtFortschritt(lektionen, fortschritt), 0.5);
});
