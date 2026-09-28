"""Fuehrt die Stimmen aus Durchlauf 1 (5 Stichproben) und Durchlauf 2 (bis zu 10
weitere Stichproben fuer Problemfaelle) pro Zeichen zusammen und trifft die
endgueltige Mehrheitsentscheidung auf Basis aller gesammelten Stimmen."""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent


def load(name):
    with open(HERE / name, encoding="utf-8") as f:
        return json.load(f)


resolved1 = load("scan_resolved.json")
unresolved1 = load("scan_unresolved.json")
resolved2 = load("scan_resolved_pass2.json")
unresolved2 = load("scan_unresolved_pass2.json")

votes_by_char = {}  # char -> Counter
all_chars_seen = set()


def add_votes(char, counter):
    all_chars_seen.add(char)
    if char not in votes_by_char:
        votes_by_char[char] = Counter()
    votes_by_char[char].update(counter)


for c, v in resolved1.items():
    add_votes(c, v["votes"])

for u in unresolved1:
    c = u["char"]
    votes = u.get("votes")
    if votes:
        add_votes(c, votes)
    else:
        all_chars_seen.add(c)  # keine_gueltige_erkennung -> trotzdem erfasst, 0 Stimmen

for c, v in resolved2.items():
    add_votes(c, v["votes"])

for u in unresolved2:
    c = u["char"]
    votes = u.get("votes")
    if votes:
        add_votes(c, votes)
    else:
        all_chars_seen.add(c)

final_resolved = {}
final_unresolved = []

# Auch die von Anfang an klar aufgeloesten Zeichen aus resolved1 uebernehmen,
# die NICHT im zweiten Durchlauf nochmal angefasst wurden (klare Faelle).
all_chars = all_chars_seen | set(votes_by_char.keys())

for c in all_chars:
    counter = votes_by_char.get(c, Counter())
    total = sum(counter.values())
    if total == 0:
        final_unresolved.append({"codepoint": f"U+{ord(c):04X}", "char": c,
                                  "reason": "keine_gueltige_erkennung", "votes": {}})
        continue
    top_char, top_count = counter.most_common(1)[0]
    ratio = top_count / total
    if ratio >= 0.6:
        final_resolved[c] = {
            "correct": top_char, "votes": dict(counter), "n_votes": total,
            "unanimous": len(counter) == 1, "ratio": round(ratio, 3),
        }
    else:
        final_unresolved.append({"codepoint": f"U+{ord(c):04X}", "char": c,
                                  "reason": "uneindeutig", "votes": dict(counter)})

print(f"Endgueltig aufgeloest: {len(final_resolved)}")
print(f"Endgueltig ungeklaert: {len(final_unresolved)}")
unanimous_final = sum(1 for v in final_resolved.values() if v["unanimous"])
print(f"davon einstimmig: {unanimous_final}, mehrheitlich: {len(final_resolved) - unanimous_final}")

with open(HERE / "scan_final_resolved.json", "w", encoding="utf-8") as f:
    json.dump(final_resolved, f, ensure_ascii=False, indent=2)
with open(HERE / "scan_final_unresolved.json", "w", encoding="utf-8") as f:
    json.dump(final_unresolved, f, ensure_ascii=False, indent=2)

print("Fertig: scan_final_resolved.json / scan_final_unresolved.json")
