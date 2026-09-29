// Gemeinsamer Helfer für lokale Kalendertage. `toISOString()` rechnet in UTC und liefert
// kurz nach Mitternacht in unserer Zeitzone noch das falsche (gestrige) Datum — deshalb
// wird hier bewusst mit den lokalen Date-Gettern gearbeitet.

export function lokalesDatum(datum = new Date()) {
  const jahr = datum.getFullYear();
  const monat = String(datum.getMonth() + 1).padStart(2, "0");
  const tag = String(datum.getDate()).padStart(2, "0");
  return `${jahr}-${monat}-${tag}`;
}

// Anzahl Kalendertage von datumA zu datumB (beide "YYYY-MM-DD"), positiv wenn datumB
// später liegt. Rechnung über Date.UTC, damit Zeitzonen-/Sommerzeit-Umstellungen die
// Differenz nicht verfälschen.
export function tageDifferenz(datumA, datumB) {
  const [jA, mA, tA] = datumA.split("-").map(Number);
  const [jB, mB, tB] = datumB.split("-").map(Number);
  const utcA = Date.UTC(jA, mA - 1, tA);
  const utcB = Date.UTC(jB, mB - 1, tB);
  return Math.round((utcB - utcA) / 86400000);
}
