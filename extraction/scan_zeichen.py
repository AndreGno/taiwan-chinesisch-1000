"""Scannt die Lektionsseiten nach kaputten CJK-Ext-A-Zeichen (U+3400-U+4DBF), zieht
Stichproben-Crops pro Zeichen, erkennt sie per Tesseract-OCR und ermittelt per
Mehrheitsentscheid die korrekte Zuordnung. Schreibt Zwischenergebnisse als JSON,
damit der Vorgang nachvollziehbar bleibt (nicht Teil der Laufzeit-App)."""
import fitz
import json
import os
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

PDF_PATH = r"D:\(x)Taiwan CN DE Lernen\1000zhtw_de.pdf"
FIRST_PAGE = 8
LAST_PAGE = 157  # inclusive
MAX_SAMPLES = 5
HERE = Path(__file__).parent
CROPS_DIR = HERE / "crops"
TESSDATA_PREFIX = str(HERE / ".." / ".tessdata")
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def collect_occurrences():
    doc = fitz.open(PDF_PATH)
    occurrences = defaultdict(list)  # char -> list of (page_idx, bbox, font)
    for page_idx in range(FIRST_PAGE, LAST_PAGE + 1):
        page = doc[page_idx]
        raw = page.get_text("rawdict")
        for block in raw.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font = span.get("font", "?")
                    for ch in span.get("chars", []):
                        cp = ord(ch["c"])
                        if 0x3400 <= cp <= 0x4DBF:
                            occurrences[ch["c"]].append((page_idx, ch["bbox"], font))
    doc.close()
    return occurrences


def pick_samples(occurrences):
    samples = {}
    for c, occ in occurrences.items():
        n = len(occ)
        if n <= MAX_SAMPLES:
            samples[c] = occ
        else:
            step = n / MAX_SAMPLES
            samples[c] = [occ[int(i * step)] for i in range(MAX_SAMPLES)]
    return samples


def make_crops(samples):
    CROPS_DIR.mkdir(exist_ok=True)
    doc = fitz.open(PDF_PATH)
    crop_index = []  # list of dicts: {path, char, page, font}
    matrix = fitz.Matrix(6, 6)
    for c, occ in samples.items():
        cp = ord(c)
        for i, (page_idx, bbox, font) in enumerate(occ):
            page = doc[page_idx]
            rect = fitz.Rect(bbox)
            pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
            fname = f"U{cp:04X}_{i}.png"
            fpath = CROPS_DIR / fname
            pix.save(str(fpath))
            crop_index.append({"path": str(fpath), "char": c, "codepoint": f"U+{cp:04X}",
                                "page": page_idx, "font": font})
    doc.close()
    return crop_index


def run_ocr(crop_index):
    filelist_path = CROPS_DIR / "filelist.txt"
    with open(filelist_path, "w", encoding="utf-8") as f:
        for entry in crop_index:
            f.write(entry["path"] + "\n")

    out_base = str(CROPS_DIR / "ocr_out")
    env = dict(os.environ)
    env["TESSDATA_PREFIX"] = TESSDATA_PREFIX
    subprocess.run(
        [TESSERACT_EXE, str(filelist_path), out_base, "-l", "chi_tra", "--psm", "10",
         "-c", "tessedit_create_tsv=1"],
        check=True, env=env, capture_output=True, text=True,
    )

    tsv_path = out_base + ".tsv"
    results_by_page_num = defaultdict(list)  # page_num -> list of (text, conf)
    with open(tsv_path, "r", encoding="utf-8") as f:
        header = f.readline().strip().split("\t")
        idx = {name: i for i, name in enumerate(header)}
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                continue
            page_num = int(parts[idx["page_num"]])
            text = parts[idx["text"]]
            conf = parts[idx["conf"]]
            if text.strip():
                results_by_page_num[page_num].append((text.strip(), conf))

    for i, entry in enumerate(crop_index):
        page_num = i + 1  # tesseract page_num is 1-indexed
        texts = results_by_page_num.get(page_num, [])
        entry["ocr_texts"] = texts
        # Nur das Wort mit der hoechsten Konfidenz zaehlt als Haupt-Zeichen-Erkennung;
        # oft erkennt Tesseract im Crop zusaetzlich einen benachbarten Zhuyin-Annotationsstrich
        # als zweites "Wort" (z.B. "%", "之"), der die Mehrheitsauswertung verfaelschen wuerde.
        if texts:
            best_text, best_conf = max(texts, key=lambda t: float(t[1]))
            entry["best_text"] = best_text
            entry["best_conf"] = float(best_conf)
        else:
            entry["best_text"] = None
            entry["best_conf"] = None
    return crop_index


def evaluate(crop_index):
    by_char = defaultdict(list)
    for entry in crop_index:
        by_char[entry["char"]].append(entry)

    resolved = {}
    unresolved = []
    for c, entries in by_char.items():
        votes = []
        for e in entries:
            text = e.get("best_text")
            if text and len(text) == 1 and 0x4E00 <= ord(text) <= 0x9FFF:
                votes.append(text)
        if not votes:
            unresolved.append({"codepoint": f"U+{ord(c):04X}", "char": c, "reason": "keine_gueltige_erkennung",
                                "entries": entries})
            continue
        counter = Counter(votes)
        top_char, top_count = counter.most_common(1)[0]
        if top_count / len(votes) >= 0.6:
            resolved[c] = {
                "correct": top_char, "votes": dict(counter), "n_samples": len(entries),
                "unanimous": len(counter) == 1,
            }
        else:
            unresolved.append({"codepoint": f"U+{ord(c):04X}", "char": c, "reason": "uneindeutig",
                                "votes": dict(counter), "entries": entries})
    return resolved, unresolved


def main():
    print("Sammle Vorkommen...")
    occurrences = collect_occurrences()
    print(f"{len(occurrences)} verschiedene kaputte Zeichen, {sum(len(v) for v in occurrences.values())} Vorkommen")

    samples = pick_samples(occurrences)
    print("Erzeuge Crops...")
    crop_index = make_crops(samples)
    print(f"{len(crop_index)} Crops erzeugt")

    print("Starte Tesseract OCR (Batch)...")
    crop_index = run_ocr(crop_index)

    print("Werte aus...")
    resolved, unresolved = evaluate(crop_index)
    print(f"Aufgelöst: {len(resolved)}, ungeklärt: {len(unresolved)}")

    with open(HERE / "scan_resolved.json", "w", encoding="utf-8") as f:
        json.dump({c: v for c, v in resolved.items()}, f, ensure_ascii=False, indent=2)
    with open(HERE / "scan_unresolved.json", "w", encoding="utf-8") as f:
        json.dump(unresolved, f, ensure_ascii=False, indent=2)

    print("Fertig. scan_resolved.json / scan_unresolved.json geschrieben.")


if __name__ == "__main__":
    main()
