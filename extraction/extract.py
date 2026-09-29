"""Erzeugt data/lektionen.json und data/lektion-NN.json aus dem 1000-Wörter-PDF.

Aufruf:  python extraction/extract.py [Lektionsnummern ...]
Ohne Nummern werden alle 75 Lektionen geschrieben (bestehende Dateien werden
überschrieben). Hinweise des Parsers landen auf der Konsole.
"""

import json
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from lektion_parser import parse_lektion  # noqa: E402

PDF = Path(r"D:\(x)Taiwan CN DE Lernen\1000zhtw_de.pdf")
DATA = Path(__file__).parent.parent / "data"
ERSTE_SEITE = 8  # 0-basiert: Lektion N = Seiten 8+2(N-1) und 9+2(N-1)
ANZAHL = 75


def schreiben(pfad: Path, daten) -> None:
    pfad.write_text(json.dumps(daten, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(nummern: list[int]) -> None:
    doc = pymupdf.open(PDF)
    alle = not nummern
    uebersicht = []
    for n in nummern or range(1, ANZAHL + 1):
        s = ERSTE_SEITE + 2 * (n - 1)
        lektion, hinweise = parse_lektion(
            n, doc[s].get_text("rawdict"), doc[s + 1].get_text("rawdict"))
        schreiben(DATA / f"lektion-{n:02d}.json", lektion)
        uebersicht.append({k: lektion[k] for k in ("nummer", "titel_zh", "titel_de")})
        for h in hinweise:
            print(f"Lektion {n}: {h}")
    if alle:
        schreiben(DATA / "lektionen.json", uebersicht)


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]])
