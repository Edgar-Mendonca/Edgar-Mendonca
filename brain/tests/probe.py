"""Routing probes: plain-language tasks and the project they belong to.
Prints whether the top project is right, and '+' when a note from that project is among the top 3 related notes."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from brain import Brain  # noqa: E402

b = Brain()
probes = json.loads((HERE / "probes.json").read_text())
hits = found = 0
for q, want in probes:
    r = b.ask(q, k=3)
    got = r["answer"][0]
    ok = got[0] == want
    near = any(x["project"] == want for x in r["related"])
    hits += ok
    found += near
    print(f"{'ok  ' if ok else 'MISS'} {'+' if near else ' '} {want:24s} → {got[0]} {got[1]:.0%}   {q}")
print(f"{hits}/{len(probes)} routed to the right project; {found}/{len(probes)} with a related note from it in the top 3")
