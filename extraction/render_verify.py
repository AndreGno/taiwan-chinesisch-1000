"""Rendert fuer eine Auswahl von Zeichen (verify_picks.json) die jeweilige PDF-Seite
als PNG samt Markierung der Zeichen-Position, damit die Zuordnung optisch gegen den
Originaltext geprueft werden kann."""
import fitz
import json
from pathlib import Path

HERE = Path(__file__).parent
PDF_PATH = r"D:\(x)Taiwan CN DE Lernen\1000zhtw_de.pdf"
FIRST_PAGE = 8
LAST_PAGE = 157

with open(HERE / "verify_picks.json", encoding="utf-8") as f:
    picks = json.load(f)

doc = fitz.open(PDF_PATH)

# Erste Vorkommensseite pro Zeichen finden
occ_page = {}
for page_idx in range(FIRST_PAGE, LAST_PAGE + 1):
    page = doc[page_idx]
    raw = page.get_text("rawdict")
    for block in raw.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                for ch in span.get("chars", []):
                    c = ch["c"]
                    if c in picks and c not in occ_page:
                        occ_page[c] = (page_idx, ch["bbox"])

out_dir = HERE / "verify_pages"
out_dir.mkdir(exist_ok=True)

pages_to_render = {}
for c, (page_idx, bbox) in occ_page.items():
    pages_to_render.setdefault(page_idx, []).append((c, bbox))

matrix = fitz.Matrix(2, 2)
for page_idx, entries in pages_to_render.items():
    page = doc[page_idx]
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    # Rahmen um die Zeichen einzeichnen
    page_copy = doc[page_idx]
    shape = page_copy.new_shape()
    for c, bbox in entries:
        rect = fitz.Rect(bbox)
        shape.draw_rect(rect)
    shape.finish(color=(1, 0, 0), width=1.5)
    shape.commit()
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    fname = out_dir / f"page_{page_idx}.png"
    pix.save(str(fname))
    print(f"page {page_idx}: {[ (c, f'U+{ord(c):04X}', picks[c]['correct']) for c,_ in entries]}")

print("Fertig, Bilder in", out_dir)
