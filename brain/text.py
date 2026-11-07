"""Text to numbers: words and word pairs, hashed into a fixed number of buckets, weighted by TF-IDF.

Hashing keeps the input layer a fixed size, so new words (a new app, a new client) never break a trained model.
"""
from __future__ import annotations

import re
import zlib

import numpy as np

DIM = 1 << 13          # 8192 input buckets
STOP = set("""a an and are as at be been but by can do does each for from has have how if in into is it its
of on or so such than that the their them then there these they this to was we were what when where which while
who will with without you your our not no all any also more most other some only same very just one two may""".split())
TOKEN = re.compile(r"[a-z][a-z0-9+#.\-]*[a-z0-9+#]|[a-z]|\d+(?:\.\d+)*")


def tokens(text: str) -> list[str]:
    words = [w for w in TOKEN.findall(text.lower()) if w not in STOP and len(w) > 1]
    return words + [f"{a}_{b}" for a, b in zip(words, words[1:])]


def bucket(tok: str) -> int:
    return zlib.crc32(tok.encode()) % DIM


def counts(text: str) -> dict[int, float]:
    out: dict[int, float] = {}
    for t in tokens(text):
        b = bucket(t)
        out[b] = out.get(b, 0.0) + 1.0
    return out


class Vectorizer:
    """log(1 + term count) × IDF, then unit length. Fitted once on the corpus; stored with the model."""

    def __init__(self, idf: np.ndarray | None = None):
        self.idf = idf

    def fit(self, texts: list[str]) -> "Vectorizer":
        df = np.zeros(DIM, dtype=np.float64)
        for t in texts:
            for b in counts(t):
                df[b] += 1
        n = len(texts)
        self.idf = (np.log((1 + n) / (1 + df)) + 1).astype(np.float32)
        return self

    def sparse(self, text: str) -> tuple[np.ndarray, np.ndarray]:
        c = counts(text)
        if not c:
            return np.zeros(0, np.int32), np.zeros(0, np.float32)
        idx = np.fromiter(c.keys(), np.int32, len(c))
        val = np.log1p(np.fromiter(c.values(), np.float32, len(c))) * self.idf[idx]
        return idx, (val / (np.linalg.norm(val) + 1e-9)).astype(np.float32)

    def dense(self, texts: list[str]) -> np.ndarray:
        X = np.zeros((len(texts), DIM), dtype=np.float32)
        for i, t in enumerate(texts):
            idx, val = self.sparse(t)
            X[i, idx] = val
        return X
