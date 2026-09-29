import test from "node:test";
import assert from "node:assert/strict";
import { exportSchluessel } from "./fortschritt.js";

test("exportSchluessel enthält genau die drei zh1000-Schlüssel", () => {
  assert.deepEqual(exportSchluessel(), [
    "zh1000-fortschritt",
    "zh1000-karteikarten-status",
    "zh1000-streak-status",
  ]);
});
