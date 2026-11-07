"""The network, written from scratch in NumPy: forward pass, backpropagation and the Adam optimiser.

    input (8192 hashed TF-IDF features)
      → dense 512, ReLU, dropout          ┐ hidden layers: "what is this text about"
      → dense 256, ReLU, dropout          ┘ (any number of them; sizes set when training)
      → dense 128, tanh                   the embedding: one point in Edgar's work-space
      → three softmax heads, trained together:
           project  (datum-pipe, centriforge, shpb, standards, ...)
           area     (piping, rotating-equipment, impact-mechanics, ...)
           kind     (decision, release, plan, standard, note, ...)

Training the three heads together makes the shared embedding organise the text by all three at once, so texts
that are close in the embedding are close in subject, in project and in the sort of knowledge they hold.

Parameter names: W1, b1 … Wn, bn for the hidden layers; We, be for the embedding; W_<head>, b_<head> for each head.
brain/torch_brain.py loads the same weights into PyTorch.
"""
from __future__ import annotations

import numpy as np

HEADS = ("project", "area", "kind")


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


class Net:
    def __init__(self, n_in: int, sizes: dict[str, int], hidden: tuple[int, ...] = (512, 256), emb: int = 128, seed: int = 7):
        rng = np.random.default_rng(seed)

        def he(i, o):
            return (rng.standard_normal((i, o)) * np.sqrt(2.0 / i)).astype(np.float32)

        def xavier(i, o):
            return (rng.standard_normal((i, o)) * np.sqrt(1.0 / i)).astype(np.float32)

        self.p: dict[str, np.ndarray] = {}
        dims = [n_in, *hidden]
        for k in range(len(hidden)):
            self.p[f"W{k + 1}"] = he(dims[k], dims[k + 1])
            self.p[f"b{k + 1}"] = np.zeros(dims[k + 1], np.float32)
        self.p["We"] = xavier(dims[-1], emb)
        self.p["be"] = np.zeros(emb, np.float32)
        for h, n in sizes.items():
            self.p[f"W_{h}"] = xavier(emb, n)
            self.p[f"b_{h}"] = np.zeros(n, np.float32)
        self.depth = len(hidden)
        self.heads = list(sizes)
        self.m = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.v = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.t = 0

    @property
    def shape(self) -> list[int]:
        return [self.p["W1"].shape[0]] + [self.p[f"W{k + 1}"].shape[1] for k in range(self.depth)] + [self.p["We"].shape[1]]

    # ---------- forward ----------

    def forward(self, X: np.ndarray, train: bool = False, drop: float = 0.3, rng=None):
        """Returns the heads' probabilities and a cache: the inputs, each hidden layer's pre-activation (z),
        activation (a) and dropout mask, and the embedding (e)."""
        p, a, zs, acts, masks = self.p, X, [], [], []
        for k in range(1, self.depth + 1):
            z = a @ p[f"W{k}"] + p[f"b{k}"]
            a = np.maximum(z, 0)
            mask = None
            if train and drop > 0:
                mask = (rng.random(a.shape) > drop).astype(np.float32) / (1 - drop)
                a = a * mask
            zs.append(z); acts.append(a); masks.append(mask)
        e = np.tanh(a @ p["We"] + p["be"])
        probs = {h: softmax(e @ p[f"W_{h}"] + p[f"b_{h}"]) for h in self.heads}
        return probs, {"x": X, "z": zs, "a": acts, "mask": masks, "e": e}

    def embed(self, X: np.ndarray, batch: int = 512) -> np.ndarray:
        return np.vstack([self.forward(X[i:i + batch])[1]["e"] for i in range(0, len(X), batch)])

    # ---------- backward ----------

    def grads(self, X: np.ndarray, Y: dict[str, np.ndarray], weights: dict[str, np.ndarray], rng=None,
              head_w: dict[str, float] | None = None, drop: float = 0.3) -> tuple[float, dict[str, np.ndarray]]:
        """Loss and gradients by backpropagation: summed, class-weighted cross-entropy of the heads.
        With rng=None there is no dropout, which makes the result deterministic (used by the gradient check)."""
        head_w = head_w or {}
        probs, c = self.forward(X, train=rng is not None, drop=drop, rng=rng)
        n, e = X.shape[0], c["e"]
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
        dz = de * (1 - e * e)
        a_last = c["a"][-1]
        g["We"] = a_last.T @ dz
        g["be"] = dz.sum(0)
        da = dz @ self.p["We"].T
        for k in range(self.depth, 0, -1):
            if c["mask"][k - 1] is not None:
                da = da * c["mask"][k - 1]
            dzk = da * (c["z"][k - 1] > 0)
            a_prev = c["a"][k - 2] if k > 1 else c["x"]
            g[f"W{k}"] = a_prev.T @ dzk
            g[f"b{k}"] = dzk.sum(0)
            if k > 1:
                da = dzk @ self.p[f"W{k}"].T
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
        net.depth = sum(1 for k in net.p if k[0] == "W" and k[1:].isdigit())
        net.heads = heads
        return net
