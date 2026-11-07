"""Routing probes for the private build (questions in brain/private/probes.json; never committed)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.argv.append("--private")
sys.path.insert(0, str(HERE.parent))
from brain import Brain, HOME  # noqa: E402
b = Brain()
probes = json.loads((HOME / "probes.json").read_text())
hits = 0
for q, want in probes:
    r = b.ask(q, k=3)
    got = r["project"][0][0]
    found = any(x["project"] == want for x in r["related"])
    hits += got == want
    print(f"{'ok  ' if got == want else 'MISS'} {'+' if found else ' '} {want:22s} → {got:22s} {q[:60]}")
print(f"{hits}/{len(probes)} routed; '+' = a related note from the right project in the top 3")
