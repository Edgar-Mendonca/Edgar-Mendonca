"""Build the brain viewer: one self-contained HTML page with the map of the corpus and the network itself.

    python brain/viewer.py            # writes brain/model/viewer.html (not committed: it is a private page)
    python brain/viewer.py --private  # the private build: writes brain/private/model/viewer.html

The page runs the trained network in the browser (same tokenizer, hashing, TF-IDF and layers as brain.py), so the
Ask box gives the same answers as `brain.py ask`. The map places every chunk by its 64-number embedding, laid out
in 2D with t-SNE (written here in NumPy).
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from brain import CORPUS, HOME, MODEL, REPORT, load_corpus  # noqa: E402
from text import DIM, STOP  # noqa: E402

OUT = HOME / "model" / "viewer.html"
TEMPLATE = HERE / "viewer_template.html"


def tsne(X: np.ndarray, perplexity: float = 30, iters: int = 750, seed: int = 0) -> np.ndarray:
    """Exact t-SNE on cosine distances: keeps neighbours in the embedding as neighbours on the map."""
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    n = len(X)
    D = np.maximum(2 - 2 * X @ X.T, 0)
    P = np.zeros((n, n))
    target = np.log(perplexity)
    for i in range(n):
        lo, hi, beta = 0.0, np.inf, 1.0
        d = np.delete(D[i], i)
        for _ in range(50):
            p = np.exp(-d * beta)
            s = p.sum() + 1e-12
            H = np.log(s) + beta * (d * p).sum() / s
            if abs(H - target) < 1e-5:
                break
            if H > target:
                lo, beta = beta, beta * 2 if hi == np.inf else (beta + hi) / 2
            else:
                hi, beta = beta, (beta + lo) / 2
        P[i, np.arange(n) != i] = p / s
    P = np.maximum((P + P.T) / (2 * n), 1e-12)
    rng = np.random.default_rng(seed)
    Y = rng.standard_normal((n, 2)) * 1e-4
    V = np.zeros_like(Y)
    gains = np.ones_like(Y)
    for it in range(iters):
        exag = 12 if it < 200 else 1
        s = (Y * Y).sum(1)
        num = 1 / (1 + s[:, None] + s[None, :] - 2 * Y @ Y.T)
        np.fill_diagonal(num, 0)
        Q = np.maximum(num / num.sum(), 1e-12)
        W = (exag * P - Q) * num
        G = 4 * ((np.diag(W.sum(1)) - W) @ Y)
        mom = 0.5 if it < 250 else 0.8
        gains = np.maximum((gains + 0.2) * ((G > 0) != (V > 0)) + gains * 0.8 * ((G > 0) == (V > 0)), 0.01)
        V = mom * V - 200 * gains * G
        Y += V
        Y -= Y.mean(0)
    return Y


def b64(a: np.ndarray) -> str:
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def r(a, n=5):
    return [round(float(x), n) for x in np.asarray(a).ravel()]


def build() -> Path:
    z = np.load(MODEL, allow_pickle=False)
    labels = json.loads(str(z["labels"]))
    p = {k[2:]: z[k].astype(np.float32) for k in z.files if k.startswith("p_")}
    rows = load_corpus()
    emb = z["emb"].astype(np.float32)
    if len(rows) != len(emb):
        sys.exit("The corpus changed since training: run  python brain/brain.py train")
    report = json.loads(REPORT.read_text())
    sources = json.loads((HERE / "sources.json").read_text())

    print(f"laying out {len(rows)} chunks with t-SNE …")
    Y = tsne(emb)
    Y = (Y - Y.min(0)) / (Y.max(0) - Y.min(0))

    # First layer, 8192 × 128: 8-bit with one scale per hidden unit (the rest is small enough to ship as is).
    W1 = p["W1"]
    s1 = np.abs(W1).max(0) / 127 + 1e-12
    q1 = np.clip(np.round(W1 / s1), -127, 127).astype(np.int8)
    embn = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-9)
    qe = np.clip(np.round(embn * 127), -127, 127).astype(np.int8)

    def repo_url(src: str) -> str:
        if src.startswith("private/"):
            return ""                                  # private sources have no public page
        if src.startswith("local/"):
            return "https://github.com/Edgar-Mendonca/Edgar-Mendonca/blob/HEAD/" + src[len("local/"):]
        owner, repo, path = src.split("/", 2)
        return f"https://github.com/{owner}/{repo}/blob/HEAD/{path}"

    data = {
        "dim": DIM, "stop": sorted(STOP), "labels": labels, "report": {k: v for k, v in report.items() if k != "labels"},
        "areas": sources["areas"], "generated": str(np.datetime64("today")),
        "idf": r(z["idf"].astype(np.float32), 4),
        "W1": b64(q1), "s1": r(s1, 8), "b1": r(p["b1"]), "W2": r(p["W2"]), "b2": r(p["b2"]),
        "heads": {h: {"W": r(p[f"W_{h}"]), "b": r(p[f"b_{h}"]), "n": len(labels[h])} for h in labels},
        "hidden": int(p["b1"].size), "embDim": int(p["b2"].size),
        "emb": b64(qe),
        "rows": [{"p": x["project"], "a": x["area"], "k": x["kind"], "s": x["source"], "u": repo_url(x["source"]),
                  "h": x["heading"], "v": x["version"], "d": x["date"], "t": x["text"],
                  "x": round(float(Y[i, 0]), 4), "y": round(float(Y[i, 1]), 4)} for i, x in enumerate(rows)],
    }
    html = TEMPLATE.read_text(encoding="utf-8").replace("__BRAIN_DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(HERE.parent)} ({OUT.stat().st_size / 1e6:.1f} MB)")
    return OUT


if __name__ == "__main__":
    build()
