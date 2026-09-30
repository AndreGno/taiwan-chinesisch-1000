import { sprich, stoppSprache } from "./tts.js";
import { escapeHtml } from "./app.js";
import { mische, erzeugeOptionen } from "./hoerverstehen.js";

export function quizVokabeln(vokabeln) {
  return vokabeln.filter((v) => v.zh && v.de);
}

// Antworten mit derselben Anzeige wie die richtige (z. B. zwei Vokabeln mit der
// Bedeutung "du") wären nicht unterscheidbar — sie fallen als Ablenker weg.
export function quizOptionen(ziel, vokabeln, feld) {
  const gesehen = new Set([ziel[feld]]);
  const kandidaten = [ziel];
  for (const v of mische(vokabeln)) {
    if (gesehen.has(v[feld])) continue;
    gesehen.add(v[feld]);
    kandidaten.push(v);
  }
  return erzeugeOptionen(ziel, kandidaten);
}

function chinesisch(v) {
  return `${escapeHtml(v.zh)}${v.pinyin ? `<span class="pinyin">${escapeHtml(v.pinyin)}</span>` : ""}`;
}

// Richtung pro Frage zufällig: Chinesisch → Deutsch oder Deutsch → Chinesisch.
export function rendereVokabelquiz(alleVokabeln, container) {
  const vokabeln = quizVokabeln(alleVokabeln);
  const reihenfolge = mische(vokabeln);
  let index = 0;
  let richtige = 0;

  function zeigeFrage() {
    if (index >= reihenfolge.length) {
      stoppSprache();
      container.innerHTML = `<p>Quiz beendet! ${richtige} von ${reihenfolge.length} richtig.</p>`;
      return;
    }
    const ziel = reihenfolge[index];
    const zhGefragt = Math.random() < 0.5;
    const feld = zhGefragt ? "de" : "zh";
    const optionen = quizOptionen(ziel, vokabeln, feld);
    container.innerHTML = `
      <p class="hinweis-klein">Frage ${index + 1} von ${reihenfolge.length}</p>
      ${zhGefragt
        ? `<p class="zh quiz-frage">${chinesisch(ziel)} <button class="tts-knopf" id="anhoeren-vokabel" title="Vorlesen (synthetische Sprachausgabe)">🔊</button></p>
           <p>Was bedeutet das?</p>`
        : `<p class="quiz-frage">${escapeHtml(ziel.de)}</p>
           <p>Wie heißt das auf Chinesisch?</p>`}
      <ul class="quiz-optionen">
        ${optionen.map((o, i) => `<li><button data-i="${i}" ${zhGefragt ? "" : `class="zh"`}>${zhGefragt ? escapeHtml(o.de) : chinesisch(o)}</button></li>`).join("")}
      </ul>
      <p id="ergebnis"></p>
    `;
    container.querySelector("#anhoeren-vokabel")?.addEventListener("click", () => sprich(ziel.zh));
    const knoepfe = container.querySelectorAll("[data-i]");
    knoepfe.forEach((btn, i) => {
      btn.addEventListener("click", () => {
        // sofort sperren, damit ein zweiter Klick keine Frage überspringt
        knoepfe.forEach((b) => (b.disabled = true));
        const richtig = optionen[i] === ziel;
        if (richtig) richtige += 1;
        knoepfe[optionen.indexOf(ziel)].classList.add("richtig");
        if (!richtig) btn.classList.add("falsch");
        container.querySelector("#ergebnis").textContent = richtig
          ? "Richtig! ✓"
          : `Falsch — richtig: ${ziel.zh} (${ziel.pinyin}) = ${ziel.de}`;
        if (!zhGefragt) sprich(ziel.zh);
        setTimeout(() => {
          // Übung inzwischen gewechselt → nichts mehr nachschieben
          if (!btn.isConnected) return;
          index += 1;
          zeigeFrage();
        }, richtig ? 1200 : 2500);
      });
    });
  }

  zeigeFrage();
}
