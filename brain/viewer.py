"""Build the brain viewer: one self-contained page with the whole network, running in the browser.

    python brain/viewer.py            # writes brain/model/viewer.html (not committed: it is published privately)

The page draws the network as nodes and connections for any question: its words, the most active units of each
hidden layer, the strongest embedding values and the likeliest projects, each line a real weight × activation.
It runs the trained network itself (same tokenizer, hashing, TF-IDF and layers as brain.py), so its answer is the
same as `brain.py ask`. The two large weight matrices are stored as 8-bit integers with one scale per unit.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from brain import HOME, MODEL, REPORT, load_corpus  # noqa: E402
from text import DIM, STOP  # noqa: E402

OUT = HOME / "model" / "viewer.html"
TEMPLATE = HERE / "viewer_template.html"
REPO = "https://github.com/Edgar-Mendonca/Edgar-Mendonca/blob/HEAD/"


def b64(a: np.ndarray) -> str:
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def r(a, n=5):
    return [round(float(x), n) for x in np.asarray(a).ravel()]


def q8(W: np.ndarray) -> dict:
    """8-bit weights with one scale per output unit."""
    s = np.abs(W).max(0) / 127 + 1e-12
    return {"q": b64(np.clip(np.round(W / s), -127, 127).astype(np.int8)), "s": r(s, 8), "rows": int(W.shape[0]), "cols": int(W.shape[1])}


def repo_url(src: str) -> str:
    if src.startswith("private/"):
        return ""
    if src.startswith("brain/"):
        return REPO + src
    if src.startswith("local/"):
        return REPO + src[len("local/"):]
    owner, repo, path = src.split("/", 2)
    return f"https://github.com/{owner}/{repo}/blob/HEAD/{path}"


def build() -> Path:
    z = np.load(MODEL, allow_pickle=False)
    labels = json.loads(str(z["labels"]))
    p = {k[2:]: z[k].astype(np.float32) for k in z.files if k.startswith("p_")}
    depth = sum(1 for k in p if k[0] == "W" and k[1:].isdigit())
    rows = load_corpus()
    emb = z["emb"].astype(np.float32)
    if len(rows) != len(emb):
        sys.exit("The corpus changed since training: run  python brain/brain.py train")
    report = json.loads(REPORT.read_text())
    sources = json.loads((HERE / "sources.json").read_text())
    embn = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)
    data = {
        "dim": DIM, "stop": sorted(STOP), "labels": labels, "areas": sources["areas"],
        "report": {k: v for k, v in report.items() if k not in ("labels", "history")},
        "generated": str(np.datetime64("today")),
        "idf": r(z["idf"].astype(np.float32), 4),
        "layers": [{**q8(p[f"W{k}"]), "b": r(p[f"b{k}"])} for k in range(1, depth + 1)],
        "We": r(p["We"]), "be": r(p["be"]), "embDim": int(p["be"].size),
        "heads": {h: {"W": r(p[f"W_{h}"]), "b": r(p[f"b_{h}"]), "n": len(labels[h])} for h in labels},
        "emb": b64(np.clip(np.round(embn * 127), -127, 127).astype(np.int8)),
        "rows": [{"p": x["project"], "a": x["area"], "k": x["kind"], "s": x["source"], "u": repo_url(x["source"]),
                  "h": x["heading"], "t": x["text"]} for x in rows],
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__BRAIN_DATA__", blob), encoding="utf-8")
    print(f"wrote {OUT.relative_to(HERE.parent)} ({OUT.stat().st_size / 1e6:.1f} MB)")
    return OUT


if __name__ == "__main__":
    build()
