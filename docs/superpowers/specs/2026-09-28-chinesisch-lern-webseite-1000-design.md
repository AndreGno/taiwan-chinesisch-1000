# Design: Interaktive Chinesisch-Lernwebseite "1000 Wörter" (zweites Projekt)

Stand: 2026-09-28. Zweites, eigenständiges Projekt neben der bereits fertigen
"500 Wörter"-App (`D:\_Projekte\Claude\ChinesischLernApp\`). Kein gemeinsames Repo,
keine Kursauswahl in der alten App — explizite Nutzerentscheidung.

## Ausgangslage

- Quelle: `D:\(x)Taiwan CN DE Lernen\1000zhtw_de.pdf` — OCAC-Lehrbuch "Mit 1000 Wörtern
  Chinesisch", 210 Seiten, chinesisch-deutsch.
- **75 Lektionen** (durchgängig 2 Seiten pro Lektion, gedruckte Seiten 1–149, verifiziert
  durch vollständiges Auszählen des Inhaltsverzeichnisses auf den PDF-Seiten 4–7).
- Ziel: interaktive, moderne Lernwebseite mit allen 75 Lektionen + Übungen
  (Karteikarten mit Spaced Repetition, Satzbau, Hörverständnis, Ausspracheübung).
  Hosting: GitHub Pages (statische Seite, kein Backend) — exakt wie beim ersten Projekt.

## Verifizierte Fakten zur Quelldatei (durch echtes Scannen, nicht vermutet)

1. **Zeichen-Kodierung:** Chinesische Zeichen sind wie im ersten Buch mit kaputten
   Font-Codepoints codiert, aber mit einem **anderen Ersatzschema** als die alte
   32-Zeichen-Tabelle des ersten Projekts. Muss während der Implementierung neu durch
   Scannen ermittelt werden (`extraction/zeichen_fix.py`, neue Tabelle).
2. **Pinyin-Kodierung:** Ab Lektion 2 durchgängig ein **Symbol-Ersatzschema für
   Ton-Vokale** — Ziffern (0–9) und einzelne ASCII-Symbole (`- = & / * # ...`) stehen
   jeweils fest für einen bestimmten Vokal+Ton (z.B. `2`→á, `1`→ā, `0`→í, `8`→è, `-`→ǐ,
   `=`→ì, `&`→ǔ, `/`→ú, `*`→ù — durch Stichproben bereits plausibilisiert, vollständige
   Tabelle folgt durch systematisches Scannen in der Implementierung). Kein einfaches
   "Silbe+Tonzahl"-Format wie `ni3 hao3`. **Lektion 1 ist ein Sonderfall** und nutzt
   bereits größtenteils korrekte Unicode-Diakritika mit vereinzelten Ausreißern (`ӽ`,
   `ԁ`, `ӿ`) — wird beim Scannen der Tabelle mit abgedeckt, nicht separat behandelt.
3. **Kein eingebettetes Audio:** 0 Audio-Streams im gesamten PDF (alle 3818 Xrefs
   geprüft) — anders als beim ersten Buch mit 247 extrahierbaren MP3s. Es gibt daher
   keinen Audio-Extraktionsschritt; Aussprache wird per Browser-TTS gelöst (siehe unten).

## Architektur

Gleicher bewährter Aufbau wie im ersten Projekt — Vanilla JS/CSS, keine Build-Schritte,
keine externen Abhängigkeiten, direkt auf GitHub Pages hostbar:

```
ChinesischLernApp1000/
  extraction/
    requirements.txt
    zeichen_fix.py       # NEU ermittelte Zeichen-Fix-Tabelle (anderes Schema als Projekt 1)
    pinyin_fix.py         # NEU: Symbol→Ton-Vokal-Tabelle für die Pinyin-Umwandlung
    lektion_parser.py     # Rohtext in Lektions-/Abschnitts-Buckets, Dialog-/Vokabel-Parser
    extract.py             # Voll-Lauf über alle 210 Seiten → data/*.json
  data/
    lektion-01.json … lektion-75.json
  js/
    app.js                 # Datenlader (wie Projekt 1)
    main.js                 # Startseite: Lektionsgrid + Export/Import-Wiring
    lektion.js               # Lektionsseite: Tabs + Übungen-Menü
    srs.js                    # Vereinfachtes SM-2 (identisch zu Projekt 1, unverändert übernehmbar)
    karteikarten.js
    satzbau.js
    hoerverstehen.js           # TTS statt Original-Audio
    aussprache.js               # TTS-Vorleseknopf ergänzt (Erkennung unverändert)
    fortschritt.js                # Export/Import, erweitert um streak-status
    streak.js                      # NEU: echte Streak-Logik
  css/
    style.css                       # NEUES Dark-Gamified-Design-System
  index.html
  lektion.html
```

**Unterschiede zu Projekt 1:**
- Zwei Fix-Tabellen statt einer (Zeichen + Pinyin-Symbole)
- Kein `extract_audio.py`
- `streak.js` neu
- 75 statt 30 Lektionen (gleiche Datenstruktur pro Lektion, nur mehr Dateien)

## Datenextraktion — Vorgehen

Wie bei Projekt 1 seitenweise Verarbeitung (bewusste Entscheidung, nicht
zeilen-/koordinatenbasiert): einfacherer Ansatz, bekanntes Restrisiko (vereinzelte
Fehlzuordnungen an Abschnittsgrenzen mitten auf einer Seite, siehe Projekt 1: dort 68
Zeilen über 17/30 Lektionen betroffen). Wird bei Bedarf wie beim ersten Projekt im
Nachhinein dokumentiert statt vorab überengineert (YAGNI).

Reihenfolge (analog Projekt 1, TDD-Stil im Implementierungsplan):
1. Zeichen-Fix-Tabelle ermitteln und verifizieren
2. Pinyin-Symbol-Fix-Tabelle ermitteln und verifizieren
3. Rohtext in Lektions-/Abschnitts-Buckets aufteilen
4. Dialogzeilen-Parser, Vokabel-Parser
5. Voll-Lauf über alle 210 Seiten, Datenqualität verifizieren (Stichprobenkontrolle
   gegen PDF-Originalseiten)

## Design-System: "Gamified Dark Mode"

Im visuellen Vergleich (4 Mockup-Richtungen) vom Nutzer eindeutig gewählt.

- **Optik:** dunkler Hintergrund, kräftige Pink/Blau-Gradient-Akzente, abgerundete
  Karten mit leichtem Glow-Schatten, Fortschrittsbalken als Gradient-Balken,
  Streak-Badge mit 🔥-Icon — angelehnt an Duolingo-Stil, aber eigenständige Farbwelt.
- **Umsetzung:** reines CSS (Custom Properties für Farb-Tokens, CSS-Transitions für
  Animationen), kein Tailwind/Alpine.js — Nutzerentscheidung für Konsistenz mit dem
  abhängigkeitsfreien Ansatz aus Projekt 1.

## Übungsformen

Gleiche 4 Übungstypen wie Projekt 1, mit TTS statt Original-Audio:

- **Karteikarten (SRS):** `js/srs.js` und die Kern-Logik werden unverändert aus Projekt
  1 übernommen (gleicher vereinfachter SM-2-Algorithmus, kein Audio-Bezug).
- **Satzbau:** unverändert, keine Audio-Abhängigkeit.
- **Hörverständnis-Quiz:** TTS (`window.speechSynthesis`, `zh-TW`-Stimme) liest den
  Zielsatz statt Original-Audio abzuspielen. Rest der Logik (Multiple-Choice,
  Fisher-Yates-Shuffle, Stale-Timeout-/Doppelklick-Schutz) unverändert aus Projekt 1
  übertragen.
- **Ausspracheübung:** Erkennung unverändert (Web Speech API `SpeechRecognition`,
  `isConnected`-Guards, Button-Sperre gegen Doppelklick — Muster aus Projekt 1). Neu:
  zusätzlicher TTS-Vorleseknopf für den Zielsatz (übernimmt die Rolle des früheren
  Original-Audio-Vergleichs).
- **Bekannte Einschränkung (bewusst akzeptiert):** Browser-TTS klingt synthetisch,
  nicht so authentisch wie echte Sprecher-Aufnahmen — unvermeidbar, da das PDF keine
  Audiodateien enthält. Wird im UI nicht verschwiegen (kein stiller Qualitätsverlust).

## Gamification & Fortschritt

- **`js/streak.js`** (neu): `localStorage`-Schlüssel `streak-status`,
  Struktur `{ letzterTag: "YYYY-MM-DD", streak: n }`. Beim Aufruf einer Lektion oder
  Übung (nicht beim bloßen Startseiten-Besuch) wird geprüft: gestern gelernt → +1,
  heute schon gezählt → unverändert, Lücke ≥2 Tage → zurück auf 1.
- **Fortschrittsbalken:** wiederverwendet die bestehende `fortschritt`-Logik aus
  `app.js` (Lektion als besucht markieren), jetzt visuell als Gradient-Balken statt
  einfachem Häkchen. Gesamt-Fortschritt auf der Startseite: besuchte Lektionen / 75.
- **Darstellung:** Streak-Badge (🔥 "X Tage") im Header, Fortschrittsbalken auf
  Startseite und pro Lektion.
- **Export/Import:** `fortschritt.js` wie in Projekt 1 (JSON-Datei runterladen/wieder
  einlesen), um den Schlüssel `streak-status` erweitert.

## Deployment

Analog zu Task 18 im ersten Projekt: eigenes neues GitHub-Repo, lokal committen,
`main`-Branch, Remote verbinden, pushen, GitHub Pages aktivieren (öffentliches Repo
nötig für den kostenlosen Plan). Wird am Ende der Umsetzung gemeinsam mit dem Nutzer
durchgeführt (Repo-Erstellung und Pages-Aktivierung sind Nutzer-Aktionen).

## Bewusst nicht umgesetzt (YAGNI)

- Keine zeilen-/koordinatenbasierte PDF-Extraktion (siehe oben, explizite
  Nutzerentscheidung für den einfacheren seitenweisen Ansatz)
- Keine echten Audio-Aufnahmen (keine im PDF vorhanden, TTS als bewusster Kompromiss)
- Keine gemeinsame Codebasis mit Projekt 1 (explizite Nutzerentscheidung für
  Trennung, trotz Duplizierung z.B. bei `srs.js`)
- Keine XP-Punkte/Level-System — nur Streak + Fortschrittsbalken, wie vom Nutzer
  bestätigt (keine zusätzliche Punkte-Mechanik gewünscht)
