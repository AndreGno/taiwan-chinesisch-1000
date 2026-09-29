"""Wandelt die Ersatzsymbole der Pinyin-Schrift im 1000-Wörter-PDF in echte Tonvokale um.

Nur auf Pinyin-Felder anwenden, nie auf chinesische oder deutsche Zeilen: Dort haben
Zeichen wie "-", "/", "=" oder "Č" eine andere Bedeutung.
"""

import re
import unicodedata

SYMBOL_MAP = {
    "0": "í", "1": "ā", "2": "á", "3": "ǎ", "4": "à",
    "5": "ē", "6": "é", "7": "ě", "8": "è", "9": "ī",
    "=": "ì", "#": "ǒ", "$": "ò", "@": "ó",
    "%": "ū", "&": "ǔ", "*": "ù", "^": "ú",
    "{": "ǚ", "}": "ǜ",
    "~": "À", "`": "Ā",
    "ġ": "'",
    # Lektion 1 nutzt eine andere Schrift mit eigenen Fehlzuordnungen.
    "Ɨ": "ā", "Č": "ě", "ӽ": "ǎ", "ԁ": "ǒ", "ӿ": "ǐ",
}

# "-" und "/" kommen in Pinyin-Zeilen auch als echte Satzzeichen vor. Als Tonvokal
# stehen sie direkt hinter einem Anlaut (qǐng, nǐ, bú, sú), "-" auch hinter "u" (shuǐ)
# und "/" hinter "i" (niú, liú).
_ANLAUTE = ("zh", "ch", "sh", "b", "p", "m", "f", "d", "t", "n", "l", "g",
            "k", "h", "j", "q", "x", "r", "z", "c", "s", "y", "w")


def _grundbuchstabe(zeichen: str) -> str:
    """Tonvokal-Ersatzsymbol oder Tonvokal -> Grundvokal ("5" -> "e", "ǐ" -> "i")."""
    zeichen = {"-": "i", "/": "u"}.get(zeichen, SYMBOL_MAP.get(zeichen, zeichen))
    return unicodedata.normalize("NFD", zeichen)[:1] if zeichen.strip() else zeichen


def _ist_tonvokal_position(davor: str, symbol: str) -> bool:
    # Ersatzsymbole davor als Vokale lesen, sonst reißt die Silbe ab ("Sh5nt-" -> "shent")
    grund = "".join(_grundbuchstabe(c) for c in davor)
    buchstaben = re.search(r"[A-Za-z]*$", grund).group().lower()
    if symbol == "-" and buchstaben.endswith("u"):
        return True
    if symbol == "/" and buchstaben.endswith("i"):
        return True
    for anlaut in _ANLAUTE:
        if buchstaben.endswith(anlaut):
            rest = buchstaben[: -len(anlaut)]
            # Davor muss eine Silbe enden: auf Vokal, auf "ng" (fēngjǐng) oder auf "n"
            # (shēntǐ). Ein "g" direkt nach "n" ist dagegen Auslaut "ng" (xīng-qí).
            if rest == "" or rest[-1] in "aeiouü" or rest.endswith("ng"):
                return True
            return rest.endswith("n") and anlaut != "g"
    return False


def fix_pinyin(text: str) -> str:
    ergebnis = []
    for i, zeichen in enumerate(text):
        if zeichen in ("-", "/"):
            if _ist_tonvokal_position(text[:i], zeichen):
                ergebnis.append("ǐ" if zeichen == "-" else "ú")
            else:
                ergebnis.append(zeichen)
        elif zeichen == "!":
            ergebnis.append(" ")
        else:
            ergebnis.append(SYMBOL_MAP.get(zeichen, zeichen))
    return re.sub(r"\s+", " ", "".join(ergebnis)).strip()
