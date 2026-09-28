"""Baut Grid-Bilder aus den Original-Crops (Ziel-Glyph, hochaufgeloest) mit dem per
OCR-Mehrheitsentscheid vorgeschlagenen Zeichen als Beschriftung, damit sich viele
unsichere Zuordnungen auf einmal visuell pruefen lassen."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
CROPS_DIRS = [HERE / "crops", HERE / "crops2"]

with open(HERE / "scan_final_resolved.json", encoding="utf-8") as f:
    resolved = json.load(f)
with open(HERE / "scan_final_unresolved.json", encoding="utf-8") as f:
    unresolved = json.load(f)

non_unanimous = [(c, v) for c, v in resolved.items() if not v["unanimous"]]
unresolved_targets = [(u["char"], {"correct": "???", "votes": u.get("votes", {}), "ratio": 0.0})
                       for u in unresolved]
targets = non_unanimous + unresolved_targets
print(f"{len(targets)} Zeichen zu pruefen (non-unanimous + unresolved)")

try:
    font = ImageFont.truetype("msyh.ttc", 40)
    font_small = ImageFont.truetype("arial.ttf", 20)
except Exception:
    font = ImageFont.load_default()
    font_small = font


def find_crop(char):
    cp = ord(char)
    for d in CROPS_DIRS:
        candidates = sorted(d.glob(f"U{cp:04X}_*.png"))
        if candidates:
            return candidates[0]
    return None


CELL_W, CELL_H = 220, 280
COLS = 8

out_dir = HERE / "verify_grids"
out_dir.mkdir(exist_ok=True)

manifest = []
batch_size = COLS * 4  # 32 pro Grid
for batch_idx in range(0, len(targets), batch_size):
    batch = targets[batch_idx:batch_idx + batch_size]
    rows = (len(batch) + COLS - 1) // COLS
    grid = Image.new("RGB", (CELL_W * COLS, CELL_H * rows), "white")
    draw = ImageDraw.Draw(grid)
    for i, (char, info) in enumerate(batch):
        col, row = i % COLS, i // COLS
        x0, y0 = col * CELL_W, row * CELL_H
        crop_path = find_crop(char)
        if crop_path:
            img = Image.open(crop_path).convert("RGB")
            img.thumbnail((CELL_W - 20, CELL_H - 100))
            grid.paste(img, (x0 + 10, y0 + 10))
        votes_str = ",".join(f"{k}:{v}" for k, v in info["votes"].items())
        draw.text((x0 + 5, y0 + CELL_H - 85), f"U+{ord(char):04X}", fill="black", font=font_small)
        draw.text((x0 + 5, y0 + CELL_H - 60), f"OCR: {votes_str}"[:26], fill="blue", font=font_small)
        draw.rectangle([x0, y0, x0 + CELL_W - 1, y0 + CELL_H - 1], outline="gray")
        manifest.append({"batch": batch_idx, "index_in_batch": i, "codepoint": f"U+{ord(char):04X}",
                          "char": char, "votes": info["votes"]})
    fname = out_dir / f"grid_{batch_idx:03d}.png"
    grid.save(fname)
    print(f"gespeichert: {fname}")

with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("Fertig.")
