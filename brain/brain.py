"""Edgar's work brain: a neural network trained on everything Edgar has built, written and decided.

    python brain/brain.py collect            # clone/refresh the sources, write data/corpus.jsonl
    python brain/brain.py train              # train the network, write model/brain.npz and model/report.json
    python brain/brain.py ask "text"         # which project and area a task belongs to, and related past work
    python brain/brain.py profile            # where the evidence of Edgar's work lies, area by area

Add --private to any command to include the private sources in brain/private/ (never committed): the corpus,
model and reports then live in brain/private/ too, so nothing trained on private material reaches the repository.
Only NumPy is needed. See brain/README.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from nn import HEADS, Net  # noqa: E402
from text import DIM, Vectorizer, bucket, tokens  # noqa: E402

# Public build: brain/data and brain/model (committed). Private build: brain/private/data and brain/private/model
# (ignored by git), chosen with --private on the command line or BRAIN_PRIVATE=1.
PRIVATE = "--private" in sys.argv or os.environ.get("BRAIN_PRIVATE") == "1"
if "--private" in sys.argv:
    sys.argv.remove("--private")
HOME = HERE / "private" if PRIVATE else HERE
CORPUS = HOME / "data" / "corpus.jsonl"
MODEL = HOME / "model" / "brain.npz"
REPORT = HOME / "model" / "report.json"
PROFILE = HOME / "model" / "PROFILE.md"
DEFAULT_CACHE = Path.home() / ".cache" / "edgar-brain" / "repos"


def load_corpus() -> list[dict]:
    return [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------------------------------------------------------------- collect

def cmd_collect(a):
    from collect import collect
    rows = collect(Path(a.cache), offline=a.offline, private=PRIVATE)
    CORPUS.parent.mkdir(parents=True, exist_ok=True)
    with CORPUS.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    by = Counter(r["project"] for r in rows)
    print(f"{len(rows)} chunks, {sum(len(r['text'].split()) for r in rows):,} words → {CORPUS.relative_to(HERE.parent)}")
    for p, n in by.most_common():
        print(f"  {p:22s} {n}")


# ---------------------------------------------------------------- train

def split(rows, frac=0.15, seed=11):
    """Hold out a share of every project's chunks, so the test covers every project."""
    rng = np.random.default_rng(seed)
    by = defaultdict(list)
    for i, r in enumerate(rows):
        by[r["project"]].append(i)
    tr, te = [], []
    for idx in by.values():
        idx = rng.permutation(idx)
        k = int(round(len(idx) * frac)) if len(idx) >= 5 else 0
        te += list(idx[:k])
        tr += list(idx[k:])
    return np.array(sorted(tr)), np.array(sorted(te))


def cmd_train(a):
    rows = load_corpus()
    texts = [r["text"] for r in rows]
    labels = {h: sorted({r[h] for r in rows}) for h in HEADS}
    Y = {h: np.array([labels[h].index(r[h]) for r in rows]) for h in HEADS}
    tr, te = split(rows)

    vec = Vectorizer().fit([texts[i] for i in tr])
    X = vec.dense(texts)

    # Questions are short, so the network also learns from short passages (two sentences) of the training notes.
    # Every project gets them: all passages of the few, long notes, standards and private archives, and two random
    # passages of each repository chunk, so "short text" never becomes a clue to one project. Held-out chunks are
    # never split.
    if a.augment:
        prng = np.random.default_rng(a.seed + 1)
        extra_t, extra_y = [], {h: [] for h in HEADS}
        for i in tr:
            sents = [x for x in re.split(r"(?<=[.;:])\s+", texts[i]) if len(x.split()) >= 4]
            pairs = [" ".join(sents[j:j + 2]) for j in range(len(sents) - 1)]
            if rows[i]["source"].startswith("Edgar-Mendonca/") and len(pairs) > 2:
                pairs = [pairs[j] for j in prng.choice(len(pairs), 2, replace=False)]
            for t in pairs:
                extra_t.append(t)
                for h in HEADS:
                    extra_y[h].append(Y[h][i])
        if extra_t:
            n0 = len(texts)
            X = np.vstack([X, vec.dense(extra_t)])
            for h in HEADS:
                Y[h] = np.concatenate([Y[h], np.array(extra_y[h], dtype=Y[h].dtype)])
            tr = np.concatenate([tr, np.arange(n0, n0 + len(extra_t))])
            print(f"augmented the training set with {len(extra_t)} short passages")

    # Class weights ~ frequency^-balance: small projects still count without being over-predicted.
    weights = {}
    for h in HEADS:
        c = np.bincount(Y[h][tr], minlength=len(labels[h])).astype(np.float64)
        w = np.maximum(c, 1) ** -a.balance
        weights[h] = w / (w[Y[h][tr]].mean())

    hidden = tuple(int(x) for x in str(a.hidden).split(","))
    net = Net(DIM, {h: len(labels[h]) for h in HEADS}, hidden=hidden, emb=a.emb, seed=a.seed)
    rng = np.random.default_rng(a.seed)
    print(f"training on {len(tr)} chunks, testing on {len(te)}; "
          f"{sum(v.size for v in net.p.values()):,} parameters")
    history = []                                   # one row per epoch: the training performance curve
    for ep in range(1, a.epochs + 1):
        lr = a.lr * (0.5 * (1 + np.cos(np.pi * (ep - 1) / a.epochs)))           # cosine decay
        order = rng.permutation(tr)
        total = 0.0
        for s in range(0, len(order), a.batch):
            b = order[s:s + a.batch]
            total += net.step(X[b], {h: Y[h][b] for h in HEADS}, weights, rng, lr=lr) * len(b)
        acc = accuracy(net, X, Y, te)
        history.append({"epoch": ep, "loss": round(total / len(tr), 4), "lr": round(float(lr), 6), **{h: round(acc[h], 4) for h in HEADS}})
        if ep == 1 or ep % 5 == 0 or ep == a.epochs:
            print(f"  epoch {ep:3d}  loss {total / len(tr):.3f}  test " + "  ".join(f"{h} {acc[h]:.1%}" for h in HEADS))

    acc = accuracy(net, X, Y, te)
    real = tr[tr < len(rows)]                     # the baseline guesses the commonest class among real notes
    base = {h: float(np.mean(Y[h][te] == np.bincount(Y[h][real]).argmax())) for h in HEADS}
    emb = net.embed(X[:len(rows)])                # one embedding per corpus chunk (not the training passages)

    # For reading the hashed features back as words: the most common token in each bucket.
    top_tok: dict[int, Counter] = defaultdict(Counter)
    for t in texts:
        for tok in tokens(t):
            if "_" not in tok:
                top_tok[bucket(tok)][tok] += 1
    vocab = np.array([top_tok[b].most_common(1)[0][0] if top_tok[b] else "" for b in range(DIM)])

    MODEL.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(MODEL, idf=vec.idf.astype(np.float16), emb=emb.astype(np.float16), vocab=vocab,
                        labels=json.dumps(labels), **{f"p_{k}": v for k, v in net.state().items()})
    report = {
        "chunks": len(rows), "train": int(len(tr)), "test": int(len(te)),
        "parameters": int(sum(v.size for v in net.p.values())),
        "architecture": f"{DIM} hashed TF-IDF → {' → '.join(f'{n} ReLU' for n in hidden)} (dropout 0.3) → {a.emb} tanh embedding → heads {', '.join(f'{h} ({len(labels[h])})' for h in HEADS)}",
        "shape": net.shape,
        "test_accuracy": {h: round(acc[h], 4) for h in HEADS},
        "majority_baseline": {h: round(base[h], 4) for h in HEADS},
        "epochs": a.epochs, "balance": a.balance, "labels": labels, "history": history,
    }
    REPORT.write_text(json.dumps(report, indent=2))
    print(f"saved {MODEL.relative_to(HERE.parent)} ({MODEL.stat().st_size / 1e6:.1f} MB){' (private)' if PRIVATE else ''}")
    print("test accuracy  " + "  ".join(f"{h} {acc[h]:.1%} (baseline {base[h]:.1%})" for h in HEADS))
    write_profile(rows, labels)


def accuracy(net, X, Y, idx):
    probs, _ = net.forward(X[idx])
    return {h: float(np.mean(probs[h].argmax(1) == Y[h][idx])) for h in HEADS}


# ---------------------------------------------------------------- load and ask

class Brain:
    def __init__(self):
        if not MODEL.exists():
            sys.exit(f"No trained model yet: run  python brain/brain.py train{' --private' if PRIVATE else ''}")
        z = np.load(MODEL, allow_pickle=False)
        self.labels = json.loads(str(z["labels"]))
        self.vec = Vectorizer(z["idf"].astype(np.float32))
        self.net = Net.from_state({k[2:]: z[k] for k in z.files if k.startswith("p_")}, list(HEADS))
        self.emb = z["emb"].astype(np.float32)
        self.emb /= np.linalg.norm(self.emb, axis=1, keepdims=True) + 1e-9
        self.vocab = z["vocab"]
        self.rows = load_corpus()
        if len(self.rows) != len(self.emb):
            sys.exit("The corpus changed since training: run  python brain/brain.py train")

    def ask(self, text: str, k: int = 6) -> dict:
        x = self.vec.dense([text])
        probs, cache = self.net.forward(x)
        q = cache["e"][0] / (np.linalg.norm(cache["e"][0]) + 1e-9)
        # Related work: closeness in the learned embedding, steadied by plain word overlap.
        idx, val = self.vec.sparse(text)
        lexical = self._lexical(idx, val) if len(idx) else np.zeros(len(self.rows), np.float32)
        score = 0.6 * (self.emb @ q) + 0.4 * lexical
        top = np.argsort(-score)[:k]
        # The answer: half the network's project probabilities, half a vote of the 5 closest notes (by similarity).
        labs = self.labels["project"]
        vote = np.zeros(len(labs))
        for t in np.argsort(-score)[:5]:
            vote[labs.index(self.rows[t]["project"])] += max(float(score[t]), 0.0)
        answer = 0.5 * probs["project"][0] + 0.5 * vote / (vote.sum() + 1e-9)
        return {
            "answer": [(labs[i], float(answer[i])) for i in np.argsort(-answer)[:3]],
            **{h: [(self.labels[h][i], float(probs[h][0][i])) for i in np.argsort(-probs[h][0])[:3]] for h in HEADS},
            "related": [{**{f: self.rows[i][f] for f in ("project", "kind", "source", "heading", "version", "date")},
                         "score": round(float(score[i]), 3), "text": self.rows[i]["text"]} for i in top],
        }

    def _lexical(self, idx, val):
        if not hasattr(self, "_X"):
            self._X = self.vec.dense([r["text"] for r in self.rows])
        q = np.zeros(DIM, np.float32)
        q[idx] = val
        return self._X @ q


def cmd_ask(a):
    b = Brain()
    r = b.ask(" ".join(a.text), k=a.k)
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return
    print(f"answer   " + "   ".join(f"{n} {p:.0%}" for n, p in r["answer"]) + "   (network + closest notes)")
    for h in HEADS:
        print(f"{h:8s} " + "   ".join(f"{n} {p:.0%}" for n, p in r[h]))
    print("\nrelated work:")
    for x in r["related"]:
        tag = " · ".join(v for v in (x["project"], x["kind"], x["version"], x["date"]) if v)
        print(f"  [{x['score']:.2f}] {tag}  —  {x['source']}")
        print(f"         {x['text'][:220]}{'…' if len(x['text']) > 220 else ''}")


# ---------------------------------------------------------------- profile

def write_profile(rows, labels):
    src = json.loads((HERE / "sources.json").read_text())
    areas = src["areas"]
    by_area = defaultdict(list)
    for r in rows:
        by_area[r["area"]].append(r)
    total_words = sum(len(r["text"].split()) for r in rows)
    lines = ["# Profile", "", "Where the evidence of Edgar's work lies, from the brain's corpus. It counts what is written down",
             "(documents, releases, decisions, research), so it measures volume of documented work, not skill.", "",
             "| Area | Share | Chunks | Releases | Decisions | Plans | Research | Projects | Dates |", "|---|--:|--:|--:|--:|--:|--:|---|---|"]
    out = []
    for area, rs in by_area.items():
        words = sum(len(r["text"].split()) for r in rs)
        rel = {(r["project"], r["version"]) for r in rs if r["kind"] == "release" and r["version"]}
        dates = sorted(r["date"] for r in rs if r["date"])
        out.append((words, area, rs, rel, dates))
    for words, area, rs, rel, dates in sorted(out, reverse=True):
        kinds = Counter(r["kind"] for r in rs)
        projects = ", ".join(p for p, _ in Counter(r["project"] for r in rs).most_common())
        span = f"{dates[0]} – {dates[-1]}" if dates else ""
        lines.append(f"| {areas.get(area, area)} | {words / total_words:.0%} | {len(rs)} | {len(rel)} | {kinds['decision']} | "
                     f"{kinds['plan']} | {kinds['research'] + kinds['note']} | {projects} | {span} |")
    PROFILE.write_text("\n".join(lines) + "\n")


def cmd_profile(a):
    if not PROFILE.exists():
        write_profile(load_corpus(), None)
    print(PROFILE.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect", help="clone or refresh the sources and rebuild the corpus")
    c.add_argument("--cache", default=str(DEFAULT_CACHE), help="where the repositories are cloned")
    c.add_argument("--offline", action="store_true", help="use the cache as it is, without git")
    c.set_defaults(fn=cmd_collect)
    t = sub.add_parser("train", help="train the network on the corpus")
    t.add_argument("--epochs", type=int, default=15)
    t.add_argument("--batch", type=int, default=64)
    t.add_argument("--lr", type=float, default=1e-3)
    t.add_argument("--hidden", default="768,384,192", help="hidden layer sizes, comma-separated")
    t.add_argument("--emb", type=int, default=128)
    t.add_argument("--seed", type=int, default=7)
    t.add_argument("--balance", type=float, default=0.5, help="class weight exponent: 0 none, 0.5 strong")
    t.add_argument("--no-augment", dest="augment", action="store_false", help="do not split notes, standards and private sections into passages")
    t.set_defaults(fn=cmd_train)
    q = sub.add_parser("ask", help="route a task and find related past work")
    q.add_argument("text", nargs="+")
    q.add_argument("-k", type=int, default=6)
    q.add_argument("--json", action="store_true", help="machine-readable output, for an agent")
    q.set_defaults(fn=cmd_ask)
    p = sub.add_parser("profile", help="the evidence of work, area by area")
    p.set_defaults(fn=cmd_profile)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
