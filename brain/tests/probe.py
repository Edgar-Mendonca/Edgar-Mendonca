"""Routing probes: plain-language tasks and the project they belong to. Prints the hit rate of the trained model."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from brain import Brain  # noqa: E402

b = Brain()
probes = json.loads((HERE / "probes.json").read_text())
hits = 0
for q, want in probes:
    got = b.ask(q, k=1)["project"][0]
    hits += got[0] == want
    print(f"{'ok  ' if got[0] == want else 'MISS'} {want:20s} → {got[0]} {got[1]:.0%}   {q}")
print(f"{hits}/{len(probes)} routed to the right project")
