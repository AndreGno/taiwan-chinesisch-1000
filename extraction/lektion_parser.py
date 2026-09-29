"""Zerlegt die zwei PDF-Seiten einer Lektion aus "Mit 1000 Wörtern Chinesisch"
in das Web-Datenformat (Titel, Dialog, Vokabeln, Grammatik).

Eingabe sind die PyMuPDF-Dicts von page.get_text("rawdict"), damit die
Funktionen ohne PDF testbar bleiben.

Aufbau einer Lektion (beide Seiten hintereinander gelesen):
  - Titelzeile "第N課 <Titel>" (22 pt), darunter "Lektion N  <deutscher Titel>"
  - Dialog: Zeile "Sprecher：Text" (Hanzi 15 pt), darunter die Pinyin-Zeile
    (10 pt), die mit dem Pinyin des Sprechers beginnt
  - Vokabeln: je Eintrag Hanzi (14 pt), Pinyin (10 pt), Deutsch (13 pt), bis zu
    drei Einträge nebeneinander; läuft teils auf Seite 2 weiter
  - optional "文化諺語 Chinesische Sprichwörter" (wird übersprungen)
  - Grammatik: Titel im Yuan-Font, darunter 說明 / 例句 / 練習
  - deutsche Dialogübersetzung "Sprecher：" + deutscher Text (14 pt)
Die Abschnittsüberschriften sind Bilder, deshalb wird nach Font und Größe
eingeordnet, nicht nach Überschriften.
"""

import re

from zeichen_fix import fix_span
from pinyin_fix import fix_pinyin

PINYIN_GROESSE = 11.5  # alles darunter ist Pinyin (Dialog und Vokabeln: 10 pt)
DIALOG_GROESSE = 14.5  # Dialog-Hanzi 15 pt, Vokabeln/Grammatik 14 pt
ZEILEN_TOLERANZ = 4.0  # Grundlinien-Abstand, bis zu dem Zeichen eine Zeile bilden
SEITENFUSS_Y = 815  # darunter steht nur die Seitenzahl
SEITEN_VERSATZ = 1000  # y-Versatz für Seite 2, damit beide Seiten eine Folge bilden

DEUTSCH_FONTS = ("TimesNewRoman", "Calibri", "ErasITC")
LEERRAUM = " 　\t"
LUECKE = "（　）"


def dekodiere_zeichen(zeichen: str, font: str) -> str:
    """Ein einzelnes PDF-Zeichen lesbar machen.

    In den DF-Fonts (Hanzi) liegen auch die ASCII-Zeichen um einen Codepoint
    verschoben: "!" = Leerzeichen, "2/" = "1.", ")" "*" = "(" ")", "@" = "?",
    "xjf" = "wie", "F.nbjm" = "E-mail", Lektion 7 "2:6:" = "1959" (am
    Seitenbild geprüft). Echte Leerzeichen gibt es dort nur vereinzelt, sie
    bleiben Leerraum. SZenKai (Zhuyin-Zeilen über dem Dialog) enthält nur
    Füllzeichen. fix_span verschiebt seit b55935f genauso, kennt aber nur die
    Fonts seiner Tabellen; ASCII geht deshalb hier nie an fix_span (sonst
    doppelte Verschiebung)."""
    if font.startswith(("DF", "SZenKai")) and ord(zeichen) < 0x80:
        verschoben = chr(ord(zeichen) - 1)
        return verschoben if verschoben > " " else " "
    return fix_span(zeichen, font)


def zeichen_aus_seite(seite: dict, y_versatz: float = 0) -> list[dict]:
    """Alle Zeichen einer Seite (rawdict) dekodiert, mit Position und Font."""
    ergebnis = []
    for block in seite["blocks"]:
        for zeile in block.get("lines", []):
            for span in zeile["spans"]:
                for ch in span["chars"]:
                    y = ch["origin"][1]
                    if y > SEITENFUSS_Y:
                        continue
                    text = dekodiere_zeichen(ch["c"], span["font"])
                    if not text:
                        continue
                    ergebnis.append({
                        "c": text, "x0": ch["bbox"][0], "x1": ch["bbox"][2],
                        "y": y + y_versatz, "font": span["font"],
                        "size": span["size"],
                    })
    return ergebnis


def zeilen_bilden(zeichen: list[dict]) -> list[list[dict]]:
    """Zeichen nach Grundlinie zu Zeilen bündeln, jede Zeile nach x sortiert."""
    zeilen = []
    for z in sorted(zeichen, key=lambda z: z["y"]):
        if zeilen and z["y"] - zeilen[-1][0]["y"] <= ZEILEN_TOLERANZ:
            zeilen[-1].append(z)
        else:
            zeilen.append([z])
    return [sorted(zeile, key=lambda z: z["x0"]) for zeile in zeilen]


def ist_deutsch_font(z: dict) -> bool:
    return z["font"].startswith(DEUTSCH_FONTS) and z["size"] >= PINYIN_GROESSE


def zeichen_art(z: dict) -> str:
    """"leer", "pinyin", "de", "satz" (Satzzeichen in deutscher Schrift, z. B.
    ein Trennstrich in einer Pinyin-Zeile), "latein" (Buchstaben in DF-Fonts)
    oder "zh"."""
    if z["c"] in LEERRAUM or not z["c"].strip():
        return "leer"
    if z["font"] == "PintoneTimes" or z["size"] < PINYIN_GROESSE:
        return "pinyin"
    if ist_deutsch_font(z):
        return "de" if z["c"].isalnum() else "satz"
    if z["c"].isascii() and z["c"].isalpha():
        return "latein"
    return "zh"


def _inhalt(zeile: list[dict]) -> list[dict]:
    return [z for z in zeile if zeichen_art(z) not in ("leer", "satz")]


def _text(zeichen: list[dict]) -> str:
    """Zeichen in x-Reihenfolge verbinden; sichtbare Lücken werden Leerzeichen."""
    teile = []
    vorher = None
    for z in zeichen:
        if vorher is not None and z["x0"] - vorher["x1"] > 1.5:
            teile.append(" ")
        teile.append(z["c"])
        vorher = z
    return "".join(teile)


# --- Textbereinigung -------------------------------------------------------

def zh_bereinigen(text: str) -> str:
    """Füllzeichen entfernen, Lücken vereinheitlichen, Pfeile absetzen."""
    text = text.replace("(", "（").replace(")", "）")
    text = re.sub(r"\.{3,}|…+", "……", text)
    # Leerraum nur zwischen lateinischen Wörtern behalten ("E-mail", "wie viel")
    text = re.sub(r"[\s　]+", " ", text)
    text = re.sub(r"(?<![A-Za-z0-9]) | (?![A-Za-z0-9])", "", text)
    text = text.replace("（）", LUECKE)
    text = re.sub(r"\s*→\s*", " → ", text)
    return text.strip()


def de_bereinigen(text: str) -> str:
    """Ligaturen ersetzen (\\x03 = fl, \\x02 = fi) und Leerraum glätten."""
    text = re.sub(r"\x03\s*", "fl", text)
    text = re.sub(r"\x02\s*", "fi", text)
    text = text.replace("　", " ")
    return re.sub(r"\s+", " ", text).strip()


def pinyin_aus_zeichen(zeichen: list[dict]) -> str:
    """Pinyin-Zeichen zu Text; nur Pinyin-Fonts laufen durch fix_pinyin.

    In PintoneTimes steht "!" (immer direkt hinter einem Buchstaben) für "ō",
    das fix_pinyin sonst als Leerraum behandeln würde ("du!shao" = duōshao).
    Zeichen aus DF-Fonts (z. B. Jahreszahl in Lektion 7) sind schon dekodiert."""
    laeufe = []  # [ist_df, [zeichen]]
    for z in zeichen:
        ist_df = z["font"].startswith("DF")
        if laeufe and laeufe[-1][0] == ist_df:
            laeufe[-1][1].append(z)
        else:
            laeufe.append([ist_df, [z]])
    teile = []
    for ist_df, zz in laeufe:
        if ist_df:
            # "，" steht hier für das Silbentrennzeichen (nǚ'ér), Zhuyin-Tonzeichen entfallen
            teile.append(re.sub(r"[ˊˇˋ˙]", "", _text(zz).replace("，", "'")))
            continue
        roh = "".join(
            "ō" if z["c"] == "!" and z["font"] == "PintoneTimes" and i > 0
            and zz[i - 1]["c"].isalpha() else z["c"]
            for i, z in enumerate(zz))
        teile.append(fix_pinyin(roh))
    text = re.sub(r"\s+", " ", " ".join(teile)).strip()
    text = re.sub(r"\s+-\s+(?=\S)", "-", text)  # "dì - yī" -> "dì-yī"
    text = re.sub(r"\s*'\s*(?=\S)", "'", text)
    text = re.sub(r"^[^\w(]+", "", text)  # verirrte Zeichen vorn (Lektion 31: "-，")
    return re.sub(r"(?<=\d) (?=\d)", "", text)


def de_anhaengen(bisher: str, neu: str) -> str:
    """Deutsche Folgezeile anhängen; "Ren-" + "ai Straße" -> "Ren-ai Straße"."""
    if bisher.endswith("-") and neu[:1].islower():
        return de_bereinigen(bisher + neu)
    return de_bereinigen(bisher + " " + neu)


def pinyin_anhaengen(bisher: str, neu: str) -> str:
    """Folgezeile anhängen; ein Trennstrich am Zeilenende verbindet die Silben."""
    if not bisher:
        return neu
    if not neu:
        return bisher
    if bisher.endswith("-"):
        return bisher[:-1].rstrip() + neu
    return bisher + " " + neu


# --- Zeilentypen -----------------------------------------------------------

def vokabeln_aus_zeile(zeile: list[dict]) -> list[dict]:
    """Eine Vokabelzeile in Einträge zerlegen (Hanzi, Pinyin, Deutsch je Eintrag).

    Buchstaben in DF-Fonts gehören hier zum Deutschen ("wie viel/e")."""
    eintraege = []
    letztes = None  # (Feld, x1) des letzten sichtbaren Zeichens
    for z in zeile:
        art = zeichen_art(z)
        if art in ("latein", "satz"):
            art = "de"
        if art == "leer":
            pass
        elif (z["font"].startswith("DF") and letztes and letztes[0] != "zh"
              and z["x0"] - letztes[1] < 2.5):
            # direkt anliegend: gehört zum laufenden Feld ("wo?", "(ein)werfen",
            # "dàbǎo-kǒufú", "Hu Shih(胡適)", Apostroph in "nǚ'ér")
            art = letztes[0]
        elif (art == "zh" and z["c"].isascii() and eintraege and eintraege[-1]["pinyin"]
              and not eintraege[-1]["de"]):
            art = "de"  # DF-Klammer vor deutschem Text: "(ein)werfen"
        if art != "leer":
            letztes = (art, z["x1"])
        if art == "zh" and (not eintraege or eintraege[-1]["pinyin"] or eintraege[-1]["de"]):
            eintraege.append({"zh": [], "pinyin": [], "de": []})
        if not eintraege:
            eintraege.append({"zh": [], "pinyin": [], "de": []})
        e = eintraege[-1]
        if art == "leer":
            # Leerraum dem Feld zuordnen, das gerade gefüllt wird
            (e["de"] or e["pinyin"] or e["zh"]).append(z)
        else:
            e[art].append(z)
    return [{
        "zh": zh_bereinigen(_text(e["zh"])),
        "pinyin": pinyin_aus_zeichen(e["pinyin"]),
        "de": de_bereinigen(_text(e["de"])),
    } for e in eintraege]


def _ist_grammatiktitel(inhalt: list[dict]) -> bool:
    yuan = [z for z in inhalt if "Yuan" in z["font"]]
    return len(yuan) * 2 > len(inhalt)


def _sprecher_teilen(text: str) -> tuple[str, str] | None:
    """"王先生：Text" -> ("王先生", "Text"), wenn der Doppelpunkt vorn steht."""
    pos = text.find("：")
    if 0 < pos <= 6:
        return text[:pos], text[pos + 1:]
    return None


def _textbeginn_x(zeile: list[dict]) -> float:
    """x-Position des ersten Zeichens nach "：" in einer Dialogzeile."""
    nach_doppelpunkt = False
    for z in zeile:
        if nach_doppelpunkt and zeichen_art(z) != "leer":
            return z["x0"]
        if z["c"] == "：":
            nach_doppelpunkt = True
    return 0.0


def _pinyin_ohne_sprecher(zeile: list[dict], textbeginn: float) -> list[dict]:
    """Pinyin-Wörter entfernen, die unter dem Sprechernamen stehen."""
    woerter, wort = [], []
    for z in zeile:
        if zeichen_art(z) == "leer" or (wort and z["x0"] - wort[-1]["x1"] > 1.5):
            if wort:
                woerter.append(wort)
            wort = [] if zeichen_art(z) == "leer" else [z]
        else:
            wort.append(z)
    if wort:
        woerter.append(wort)
    behalten = []
    for w in woerter:
        if (w[0]["x0"] + w[-1]["x1"]) / 2 >= textbeginn:
            if behalten:
                behalten.append({**w[0], "c": " "})
            behalten.extend(w)
    return behalten


def _listenzeile(liste: list[str], text: str) -> None:
    """Beispiel-/Übungszeile: "1." beginnt einen Eintrag, "→" und Folgezeilen hängen an."""
    m = re.match(r"^\d+\.\s*", text)
    if m:
        liste.append(text[m.end():])
    elif not liste:
        liste.append(text)
    elif text.startswith("→"):
        liste[-1] = zh_bereinigen(liste[-1] + " " + text)
    else:
        liste[-1] += text


def parse_lektion(nummer: int, seite1: dict, seite2: dict) -> tuple[dict, list[str]]:
    """Beide Seiten einer Lektion parsen. Liefert (Lektion, Hinweise)."""
    zeichen = zeichen_aus_seite(seite1) + zeichen_aus_seite(seite2, SEITEN_VERSATZ)
    lektion = {"nummer": nummer, "titel_zh": "", "titel_de": "",
               "dialog": [], "vokabeln": [], "grammatik": []}
    hinweise = []
    uebersetzungen = []
    abschnitt = "kopf"
    pinyin_textbeginn = None  # gesetzt, solange der Sprecher-Pinyin noch fehlt
    grammatik_feld = None
    titel_zeichen = []

    for zeile in zeilen_bilden(zeichen):
        inhalt = _inhalt(zeile)
        if not inhalt:
            continue
        arten = {zeichen_art(z) for z in inhalt}
        text_roh = _text(zeile)

        # Kopf: chinesischer und deutscher Titel
        if abschnitt == "kopf":
            if any(z["size"] > 20 for z in inhalt) and "課" in text_roh:
                lektion["titel_zh"] = zh_bereinigen(text_roh.split("課", 1)[1])
                continue
            if any(z["font"].startswith("ErasITC") for z in inhalt):
                de = de_bereinigen(_text([z for z in zeile if z["font"].startswith("ErasITC")]))
                lektion["titel_de"] = re.sub(r"^Lektion\s*\d+\s*", "", de)
                continue

        # Deutsche Dialogübersetzung: "Sprecher：" + deutscher Text am linken Rand,
        # Folgezeilen sind eingerückt und enthalten nur Deutsch
        if "de" in arten:
            de = de_bereinigen(_text([z for z in zeile if ist_deutsch_font(z)]))
            zh_teil = zh_bereinigen(_text([z for z in inhalt if zeichen_art(z) == "zh"]))
            if inhalt[0]["x0"] < 70 and zh_teil.endswith("："):
                abschnitt = "uebersetzung"
                uebersetzungen.append(de)
                continue
            if abschnitt == "uebersetzung" and arten == {"de"}:
                uebersetzungen[-1] = de_anhaengen(uebersetzungen[-1], de)
                continue

        if "文化諺語" in zh_bereinigen(text_roh):
            abschnitt = "sprichwort"
            continue

        if _ist_grammatiktitel(inhalt):
            abschnitt = "grammatik"
            vorher = lektion["grammatik"][-1] if lektion["grammatik"] else None
            if vorher and not (vorher["erklaerung"] or vorher["beispiele"] or vorher["uebungen"]):
                # Titel liegt auf zwei knapp versetzten Grundlinien (PoIn-Glyphen)
                titel_zeichen = sorted(titel_zeichen + zeile, key=lambda z: z["x0"])
                lektion["grammatik"].pop()
            else:
                titel_zeichen = zeile
            titel = re.sub(r"[：:]$", "", zh_bereinigen(_text(titel_zeichen))).strip()
            lektion["grammatik"].append(
                {"titel": titel, "erklaerung": "", "beispiele": [], "uebungen": []})
            grammatik_feld = None
            continue

        if abschnitt in ("kopf", "dialog") and "de" not in arten:
            # Trennstriche am Zeilenende stehen teils in einem DF-Font (Lektion 75)
            ascii_satz = [z for z in inhalt if z["c"].isascii() and not z["c"].isalnum()]
            if {zeichen_art(z) for z in inhalt if z not in ascii_satz} == {"pinyin"}:
                if not lektion["dialog"]:
                    hinweise.append(f"Pinyin ohne Dialogzeile: {text_roh.strip()[:30]}")
                    continue
                pz = [z for z in zeile if zeichen_art(z) != "zh" or z in ascii_satz]
                if pinyin_textbeginn is not None:
                    pz = _pinyin_ohne_sprecher(pz, pinyin_textbeginn)
                pinyin = pinyin_aus_zeichen(pz)
                if not pinyin:
                    # verirrte Einzelzeichen (Lektion 31: "-，" über der Pinyin-Zeile)
                    continue
                pinyin_textbeginn = None
                d = lektion["dialog"][-1]
                d["pinyin"] = pinyin_anhaengen(d["pinyin"], pinyin)
                continue
            if all(z["size"] > DIALOG_GROESSE for z in inhalt if zeichen_art(z) != "pinyin"):
                zh_text = zh_bereinigen(_text([z for z in inhalt if zeichen_art(z) != "pinyin"]))
                geteilt = _sprecher_teilen(zh_text)
                if geteilt:
                    abschnitt = "dialog"
                    lektion["dialog"].append(
                        {"sprecher": geteilt[0], "zh": geteilt[1], "pinyin": "", "de": ""})
                    pinyin_textbeginn = _textbeginn_x(zeile)
                elif lektion["dialog"]:
                    lektion["dialog"][-1]["zh"] += zh_text
                else:
                    hinweise.append(f"Dialogtext ohne Sprecher: {zh_text[:30]}")
                continue

        if ((abschnitt in ("kopf", "dialog", "vokabeln") and "de" in arten)
                or (abschnitt == "vokabeln" and arten & {"latein", "pinyin"})):
            abschnitt = "vokabeln"
            neue = vokabeln_aus_zeile(zeile)
            # Umgebrochener Rest der vorigen Vokabel steht vor dem nächsten Eintrag
            if neue and not neue[0]["zh"] and lektion["vokabeln"]:
                rest = neue.pop(0)
                v = lektion["vokabeln"][-1]
                v["pinyin"] = pinyin_anhaengen(v["pinyin"], rest["pinyin"])
                v["de"] = de_anhaengen(v["de"], rest["de"])
            lektion["vokabeln"].extend(neue)
            continue

        if abschnitt == "sprichwort":
            hinweise.append(f"Sprichwort übersprungen: {zh_bereinigen(text_roh)[:30]}")
            continue

        if abschnitt == "grammatik" and lektion["grammatik"]:
            punkt = lektion["grammatik"][-1]
            text = zh_bereinigen(text_roh)
            for marke, feld in (("說明：", "erklaerung"), ("例句：", "beispiele"),
                                ("練習：", "uebungen")):
                if text.startswith(marke):
                    grammatik_feld = feld
                    text = text[len(marke):].strip()
                    break
            if not text:
                continue
            if grammatik_feld == "erklaerung":
                trenner = " " if punkt["erklaerung"] and re.match(r"^\d+\.", text) else ""
                punkt["erklaerung"] += trenner + text
            elif grammatik_feld in ("beispiele", "uebungen"):
                _listenzeile(punkt[grammatik_feld], text)
            else:
                hinweise.append(f"Grammatikzeile ohne Feld: {text[:30]}")
            continue

        hinweise.append(f"Zeile nicht zugeordnet ({abschnitt}): {text_roh.strip()[:40]}")

    for i, d in enumerate(lektion["dialog"]):
        if i < len(uebersetzungen):
            d["de"] = uebersetzungen[i]
    if len(uebersetzungen) != len(lektion["dialog"]):
        hinweise.append(f"Dialogzeilen {len(lektion['dialog'])} != "
                        f"Übersetzungen {len(uebersetzungen)}")
    return lektion, hinweise
