import { ladeLektionsListe, ladeFortschritt, berechneGesamtFortschritt, rendereLektionsGrid } from "./app.js";
import { exportiereFortschritt, importiereFortschritt } from "./fortschritt.js";
import { aktuelleStreak } from "./streak.js";

const grid = document.getElementById("lektion-grid");
const streakBadge = document.getElementById("streak-badge");
const gesamtBalken = document.getElementById("gesamt-fortschritt");

// Nur anzeigen, nicht registrieren — die Streak zählt erst, wenn eine Lektion/Übung
// tatsächlich geöffnet wird (siehe lektion-main.js), nicht beim bloßen Startseitenbesuch.
streakBadge.textContent = `🔥 ${aktuelleStreak()} Tage`;

try {
  const lektionen = await ladeLektionsListe();
  const fortschritt = ladeFortschritt();
  rendereLektionsGrid(lektionen, fortschritt, grid);
  const anteil = berechneGesamtFortschritt(lektionen, fortschritt);
  gesamtBalken.style.width = `${Math.round(anteil * 100)}%`;
} catch (fehler) {
  grid.innerHTML = `<p class="fehler">${fehler.message}</p>`;
}

document.getElementById("export-btn").addEventListener("click", exportiereFortschritt);
document.getElementById("import-input").addEventListener("change", async (e) => {
  const datei = e.target.files[0];
  if (!datei) return;
  if (!confirm("Aktuellen Fortschritt mit der importierten Datei überschreiben?")) return;
  try {
    await importiereFortschritt(datei);
    location.reload();
  } catch (fehler) {
    alert(`Import fehlgeschlagen: ${fehler.message}`);
  }
});
