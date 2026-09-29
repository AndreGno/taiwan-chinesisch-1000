import test from "node:test";
import assert from "node:assert/strict";
import { normalisiereLektion } from "./app.js";
import { verfuegbareTabs, verfuegbareUebungen } from "./lektion.js";

test("verfuegbareTabs zeigt Uebungen immer, Inhalts-Tabs nur mit Daten", () => {
  const leer = normalisiereLektion({ nummer: 1 });
  assert.deepEqual(
    verfuegbareTabs(leer).map((t) => t.key),
    ["uebungen"]
  );
  const voll = normalisiereLektion({
    nummer: 1,
    dialog: [{ zh: "你好" }],
    vokabeln: [{ zh: "你" }],
    grammatik: [{ titel: "x" }],
  });
  assert.deepEqual(
    verfuegbareTabs(voll).map((t) => t.key),
    ["dialog", "vokabeln", "grammatik", "uebungen"]
  );
});

test("verfuegbareUebungen: leere Lektion deaktiviert alles", () => {
  const leer = normalisiereLektion({ nummer: 1 });
  assert.deepEqual(verfuegbareUebungen(leer), {
    karteikarten: false,
    satzbau: false,
    hoerverstehen: false,
    aussprache: false,
  });
});

test("verfuegbareUebungen: Satzbau braucht mindestens 3 Zeichen ohne Interpunktion", () => {
  const zuKurz = normalisiereLektion({ nummer: 1, dialog: [{ zh: "你，" }] });
  assert.equal(verfuegbareUebungen(zuKurz).satzbau, false);
  const langGenug = normalisiereLektion({ nummer: 1, dialog: [{ zh: "你好嗎？" }] });
  assert.equal(verfuegbareUebungen(langGenug).satzbau, true);
});

test("verfuegbareUebungen: Hoerverstehen braucht mindestens 2 vollstaendige Zeilen", () => {
  const eineZeile = normalisiereLektion({ nummer: 1, dialog: [{ zh: "你好", de: "Hallo" }] });
  assert.equal(verfuegbareUebungen(eineZeile).hoerverstehen, false);
  const zweiZeilen = normalisiereLektion({
    nummer: 1,
    dialog: [
      { zh: "你好", de: "Hallo" },
      { zh: "再見", de: "Auf Wiedersehen" },
    ],
  });
  assert.equal(verfuegbareUebungen(zweiZeilen).hoerverstehen, true);
});

test("verfuegbareUebungen: Karteikarten/Aussprache brauchen jeweils mindestens einen Eintrag", () => {
  const mitVokabel = normalisiereLektion({ nummer: 1, vokabeln: [{ zh: "你" }] });
  assert.equal(verfuegbareUebungen(mitVokabel).karteikarten, true);
  const mitDialog = normalisiereLektion({ nummer: 1, dialog: [{ zh: "你好" }] });
  assert.equal(verfuegbareUebungen(mitDialog).aussprache, true);
});
