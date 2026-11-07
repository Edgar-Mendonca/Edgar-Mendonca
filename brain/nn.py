"""The network, written from scratch in NumPy: forward pass, backpropagation and the Adam optimiser.

    input (8192 hashed TF-IDF features)
      → dense 128, ReLU, dropout          "what is this text about"
      → dense 64, tanh                    the embedding: one point in Edgar's work-space
      → three softmax heads, trained together:
           project  (datum-pipe, centriforge, shpb, ...)
           area     (piping, rotating-equipment, impact-mechanics, ...)
           kind     (decision, release, plan, research, ...)

Training the three heads together makes the shared embedding organise the text by all three at once, so texts
that are close in the embedding are close in subject, in project and in the sort of knowledge they hold.
"""
from __future__ import annotations

import numpy as np

HEADS = ("project", "area", "kind")


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class Net:
    def __init__(self, n_in: int, sizes: dict[str, int], hidden: int = 128, emb: int = 64, seed: int = 7):
        rng = np.random.default_rng(seed)

        def he(i, o):
            return (rng.standard_normal((i, o)) * np.sqrt(2.0 / i)).astype(np.float32)

        def xavier(i, o):
            return (rng.standard_normal((i, o)) * np.sqrt(1.0 / i)).astype(np.float32)

        self.p: dict[str, np.ndarray] = {
            "W1": he(n_in, hidden), "b1": np.zeros(hidden, np.float32),
            "W2": xavier(hidden, emb), "b2": np.zeros(emb, np.float32),
        }
        for h, n in sizes.items():
            self.p[f"W_{h}"] = xavier(emb, n)
            self.p[f"b_{h}"] = np.zeros(n, np.float32)
        self.heads = list(sizes)
        self.m = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.v = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.t = 0

    # ---------- forward ----------

    def forward(self, X: np.ndarray, train: bool = False, drop: float = 0.3, rng=None):
        p = self.p
        z1 = X @ p["W1"] + p["b1"]
        a1 = np.maximum(z1, 0)
        mask = None
        if train and drop > 0:
            mask = (rng.random(a1.shape) > drop).astype(np.float32) / (1 - drop)
            a1 = a1 * mask
        e = np.tanh(a1 @ p["W2"] + p["b2"])
        probs = {h: softmax(e @ p[f"W_{h}"] + p[f"b_{h}"]) for h in self.heads}
        return probs, (X, z1, a1, mask, e)

    def embed(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)[1][4]

    # ---------- backward ----------

    def grads(self, X: np.ndarray, Y: dict[str, np.ndarray], weights: dict[str, np.ndarray], rng=None,
              head_w: dict[str, float] | None = None, drop: float = 0.3) -> tuple[float, dict[str, np.ndarray]]:
        """Loss and gradients by backpropagation: summed, class-weighted cross-entropy of the heads.
        With rng=None there is no dropout, which makes the result deterministic (used by the gradient check)."""
        head_w = head_w or {}
        probs, (X, z1, a1, mask, e) = self.forward(X, train=rng is not None, drop=drop, rng=rng)
        n = X.shape[0]
        g: dict[str, np.ndarray] = {}
        de = np.zeros_like(e)
        loss = 0.0
        for h in self.heads:
            y, w, hw = Y[h], weights[h][Y[h]], head_w.get(h, 1.0)
            pr = probs[h]
            loss += hw * float(-(w * np.log(pr[np.arange(n), y] + 1e-12)).sum() / w.sum())
            d = pr.copy()
            d[np.arange(n), y] -= 1
            d *= (hw * w / w.sum())[:, None]
            g[f"W_{h}"] = e.T @ d
            g[f"b_{h}"] = d.sum(0)
            de += d @ self.p[f"W_{h}"].T
        dz2 = de * (1 - e * e)
        g["W2"] = a1.T @ dz2
        g["b2"] = dz2.sum(0)
        da1 = dz2 @ self.p["W2"].T
        if mask is not None:
            da1 *= mask
        dz1 = da1 * (z1 > 0)
        g["W1"] = X.T @ dz1
        g["b1"] = dz1.sum(0)
        return loss, g

    def step(self, X, Y, weights, rng, lr: float = 1e-3, wd: float = 1e-5, head_w=None) -> float:
        """One mini-batch of Adam (with decoupled weight decay on the weight matrices)."""
        loss, g = self.grads(X, Y, weights, rng=rng, head_w=head_w)
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for k, gk in g.items():
            self.m[k] = b1 * self.m[k] + (1 - b1) * gk
            self.v[k] = b2 * self.v[k] + (1 - b2) * gk * gk
            mh = self.m[k] / (1 - b1 ** self.t)
            vh = self.v[k] / (1 - b2 ** self.t)
            upd = lr * mh / (np.sqrt(vh) + eps)
            if k.startswith("W"):
                upd = upd + lr * wd * self.p[k]
            self.p[k] -= upd.astype(np.float32)
        return loss

    # ---------- save / load ----------

    def state(self) -> dict[str, np.ndarray]:
        return {k: v.astype(np.float16) for k, v in self.p.items()}

    @classmethod
    def from_state(cls, params: dict[str, np.ndarray], heads: list[str]) -> "Net":
        net = cls.__new__(cls)
        net.p = {k: np.asarray(v, dtype=np.float32) for k, v in params.items()}
        net.heads = heads
        return net
