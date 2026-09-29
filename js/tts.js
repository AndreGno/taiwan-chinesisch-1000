// Browser-Sprachausgabe für 台灣國語 (zh-TW). Kein Original-Audio im PDF vorhanden (siehe
// Design-Spec) — synthetische Stimme ist ein bewusster, im UI offen kommunizierter Kompromiss.

let stimmenPromise = null;

// Reine Auswahllogik, unabhängig von window/speechSynthesis testbar. Reihenfolge:
// exakt zh-TW > zh-Hant/cmn-Hant (traditionelles Chinesisch) > irgendein zh/cmn > keine.
// Android liefert Sprachcodes teils mit Unterstrich (zh_TW) statt Bindestrich.
export function waehleStimme(stimmen) {
  const kandidaten = stimmen.map((stimme) => ({
    stimme,
    lang: (stimme.lang || "").replace("_", "-").toLowerCase(),
  }));
  const exakt = kandidaten.find((k) => k.lang === "zh-tw");
  if (exakt) return exakt.stimme;
  const traditionell = kandidaten.find((k) => k.lang.includes("hant"));
  if (traditionell) return traditionell.stimme;
  const beliebig = kandidaten.find((k) => k.lang.startsWith("zh") || k.lang.startsWith("cmn"));
  if (beliebig) return beliebig.stimme;
  return null;
}

// Stimmenliste laden — im ersten Aufruf oft [] (Chrome lädt sie asynchron nach), daher
// auf "voiceschanged" warten, mit 1s-Timeout als Fallback für Browser, die das Event nie
// feuern. Wird nur einmal pro Seitenaufruf ausgeführt (Ergebnis gecacht).
function ladeStimmen() {
  if (!("speechSynthesis" in window)) return Promise.resolve([]);
  if (stimmenPromise) return stimmenPromise;
  stimmenPromise = new Promise((resolve) => {
    const vorhandene = window.speechSynthesis.getVoices();
    if (vorhandene.length) {
      resolve(vorhandene);
      return;
    }
    let erledigt = false;
    const fertig = () => {
      if (erledigt) return;
      erledigt = true;
      resolve(window.speechSynthesis.getVoices());
    };
    window.speechSynthesis.addEventListener("voiceschanged", fertig, { once: true });
    setTimeout(fertig, 1000);
  });
  return stimmenPromise;
}

export async function chinesischeStimmeVerfuegbar() {
  const stimmen = await ladeStimmen();
  return waehleStimme(stimmen) !== null;
}

// Bricht eine laufende Ausgabe ab, bevor eine neue gestartet wird — sonst stapeln sich
// Warteschlangen-Einträge bei mehrfachem Klick auf Vorlese-Knöpfe.
export async function sprich(text) {
  if (!("speechSynthesis" in window) || !text) return false;
  const stimmen = await ladeStimmen();
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "zh-TW";
  const stimme = waehleStimme(stimmen);
  if (stimme) utterance.voice = stimme;
  window.speechSynthesis.speak(utterance);
  return true;
}

export function stoppSprache() {
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}
