import { escapeHtml } from "./app.js";

const TAB_DEFS = [
  { key: "dialog", label: "對話 Dialog" },
  { key: "vokabeln", label: "字彙 Vokabeln" },
  { key: "grammatik", label: "語法 Grammatik" },
  { key: "uebungen", label: "Übungen" },
];

// "Übungen" ist ein Aktionsbereich und immer sichtbar — Dialog/Vokabeln/Grammatik nur,
// wenn für die Lektion tatsächlich Daten vorliegen (leere Abschnitte werden ausgeblendet).
export function verfuegbareTabs(lektion) {
  return TAB_DEFS.filter((tab) => {
    if (tab.key === "dialog") return lektion.dialog.length > 0;
    if (tab.key === "vokabeln") return lektion.vokabeln.length > 0;
    if (tab.key === "grammatik") return lektion.grammatik.length > 0;
    return true;
  });
}

function ohneInterpunktion(text) {
  return (text || "").replace(/[，。？！、：；,.!?;:]/g, "").trim();
}

// Schwellenwerte für "genug Daten, um die Übung sinnvoll zu starten" — Übungen ohne
// ausreichende Datenbasis werden im Menü deaktiviert statt mit einer leeren/kaputten
// Ansicht zu starten.
export function verfuegbareUebungen(lektion) {
  return {
    karteikarten: lektion.vokabeln.some((v) => v.zh),
    vokabelquiz: lektion.vokabeln.filter((v) => v.zh && v.de).length >= 4,
    satzbau: lektion.dialog.some((z) => ohneInterpunktion(z.zh).length >= 3),
    hoerverstehen: lektion.dialog.filter((z) => z.zh && z.de).length >= 2,
    aussprache: lektion.dialog.some((z) => z.zh),
  };
}

export function rendereTabs(lektion, container, aktiverTab, onWahl) {
  container.innerHTML = "";
  for (const tab of verfuegbareTabs(lektion)) {
    const btn = document.createElement("button");
    btn.textContent = tab.label;
    btn.className = tab.key === aktiverTab ? "tab aktiv" : "tab";
    btn.addEventListener("click", () => onWahl(tab.key));
    container.appendChild(btn);
  }
}

function sprichKnopf(text) {
  return `<button class="tts-knopf" data-sprich="${escapeHtml(text)}" title="Vorlesen (synthetische Sprachausgabe)">🔊</button>`;
}

function rendereSprichwort(s) {
  if (!s) return "";
  return `
      <div class="dialog-zeile sprichwort">
        <h3>文化諺語 Chinesisches Sprichwort</h3>
        <p class="zh">${escapeHtml(s.zh)} ${sprichKnopf(s.zh)}</p>
        ${s.pinyin ? `<p class="pinyin">${escapeHtml(s.pinyin)}</p>` : ""}
        ${s.de ? `<p class="de">${escapeHtml(s.de)}</p>` : ""}
      </div>`;
}

export function rendereDialog(dialog, sprichwort = null) {
  if (!dialog.length) return `<p class="hinweis">Für diese Lektion liegt noch kein Dialog vor.</p>`;
  return (
    dialog
      .map(
        (z) => `
      <div class="dialog-zeile">
        <p class="zh">${z.sprecher ? escapeHtml(z.sprecher) + "：" : ""}${escapeHtml(z.zh)} ${sprichKnopf(z.zh)}</p>
        ${z.pinyin ? `<p class="pinyin">${escapeHtml(z.pinyin)}</p>` : ""}
        ${z.de ? `<p class="de">${escapeHtml(z.de)}</p>` : ""}
      </div>`
      )
      .join("") + rendereSprichwort(sprichwort)
  );
}

export function rendereVokabeln(vokabeln) {
  if (!vokabeln.length) return `<p class="hinweis">Für diese Lektion liegen noch keine Vokabeln vor.</p>`;
  return vokabeln
    .map(
      (v) => `
      <div class="wort-zeile">
        <p class="zh">${escapeHtml(v.zh)} ${sprichKnopf(v.zh)}</p>
        ${v.pinyin ? `<p class="pinyin">${escapeHtml(v.pinyin)}</p>` : ""}
        ${v.de ? `<p class="de">${escapeHtml(v.de)}</p>` : ""}
      </div>`
    )
    .join("");
}

export function rendereGrammatik(grammatik) {
  if (!grammatik.length) return `<p class="hinweis">Für diese Lektion liegt noch keine Grammatik vor.</p>`;
  return grammatik
    .map(
      (g) => `
      <div class="grammatik-block">
        ${g.titel ? `<h3>${escapeHtml(g.titel)}</h3>` : ""}
        ${g.erklaerung ? `<p>${escapeHtml(g.erklaerung)}</p>` : ""}
        ${g.beispiele?.length ? `<ul class="beispiele">${g.beispiele.map((b) => `<li>${escapeHtml(b)}</li>`).join("")}</ul>` : ""}
        ${g.uebungen?.length ? `<ul class="uebungen-liste">${g.uebungen.map((u) => `<li>${escapeHtml(u)}</li>`).join("")}</ul>` : ""}
      </div>`
    )
    .join("");
}

export function rendereUebungenMenu(lektion) {
  const verfuegbar = verfuegbareUebungen(lektion);
  const knopf = (key, label, grund) => `
    <button data-uebung="${key}" ${verfuegbar[key] ? "" : "disabled"}>${label}</button>
    ${!verfuegbar[key] ? `<p class="hinweis-klein">${grund}</p>` : ""}`;
  return `
    <div class="uebungen-menu">
      ${knopf("karteikarten", "Karteikarten", "Keine Vokabeln vorhanden.")}
      ${knopf("vokabelquiz", "Vokabel-Quiz", "Zu wenige Vokabeln vorhanden.")}
      ${knopf("satzbau", "Satzbau", "Keine ausreichend langen Sätze vorhanden.")}
      ${knopf("hoerverstehen", "Hörverständnis", "Zu wenige vollständige Satzpaare vorhanden.")}
      ${knopf("aussprache", "Aussprache", "Kein Dialog vorhanden.")}
    </div>
    <div id="uebung-inhalt"></div>`;
}

function verdrahteTtsKnoepfe(container) {
  container.querySelectorAll("[data-sprich]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const { sprich } = await import("./tts.js");
      sprich(btn.dataset.sprich);
    });
  });
}

function verdrahteUebungenMenu(lektion, container) {
  const inhalt = container.querySelector("#uebung-inhalt");
  container.querySelectorAll("[data-uebung]:not([disabled])").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const modul = btn.dataset.uebung;
      try {
        if (modul === "karteikarten") {
          const { rendereKarteikarten } = await import("./karteikarten.js");
          if (!inhalt.isConnected) return;
          rendereKarteikarten(lektion.vokabeln, inhalt);
        } else if (modul === "vokabelquiz") {
          const { rendereVokabelquiz } = await import("./vokabelquiz.js");
          if (!inhalt.isConnected) return;
          rendereVokabelquiz(lektion.vokabeln, inhalt);
        } else if (modul === "satzbau") {
          const { rendereSatzbau } = await import("./satzbau.js");
          if (!inhalt.isConnected) return;
          rendereSatzbau(lektion.dialog, inhalt);
        } else if (modul === "hoerverstehen") {
          const { rendereHoerverstehen } = await import("./hoerverstehen.js");
          if (!inhalt.isConnected) return;
          rendereHoerverstehen(lektion.dialog, inhalt);
        } else if (modul === "aussprache") {
          const { rendereAussprache } = await import("./aussprache.js");
          if (!inhalt.isConnected) return;
          rendereAussprache(lektion.dialog, inhalt);
        }
      } catch (fehler) {
        if (!inhalt.isConnected) return;
        inhalt.innerHTML = `<p class="fehler">Übung konnte nicht geladen werden: ${escapeHtml(fehler.message)}</p>`;
      }
    });
  });
}

export function rendereTabInhalt(lektion, tabKey, container) {
  if (tabKey === "dialog") {
    container.innerHTML = rendereDialog(lektion.dialog, lektion.sprichwort);
    verdrahteTtsKnoepfe(container);
  } else if (tabKey === "vokabeln") {
    container.innerHTML = rendereVokabeln(lektion.vokabeln);
    verdrahteTtsKnoepfe(container);
  } else if (tabKey === "grammatik") {
    container.innerHTML = rendereGrammatik(lektion.grammatik);
  } else if (tabKey === "uebungen") {
    container.innerHTML = rendereUebungenMenu(lektion);
    verdrahteUebungenMenu(lektion, container);
  }
}
