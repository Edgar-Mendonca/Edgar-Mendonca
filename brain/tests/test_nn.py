"""Checks that backpropagation in nn.py is right: analytic gradients against finite differences."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from nn import Net  # noqa: E402


def test_gradients_match_finite_differences():
    rng = np.random.default_rng(0)
    net = Net(n_in=12, sizes={"project": 4, "area": 3, "kind": 2}, hidden=(8, 6), emb=5, seed=1)
    for k in net.p:                                    # check in float64 so differences are meaningful
        net.p[k] = net.p[k].astype(np.float64) + (rng.standard_normal(net.p[k].shape) * 0.1 if k.startswith("b") else 0)
    X = rng.random((6, 12))
    Y = {"project": rng.integers(0, 4, 6), "area": rng.integers(0, 3, 6), "kind": rng.integers(0, 2, 6)}
    W = {"project": np.array([1.0, 2.0, 0.5, 1.0]), "area": np.ones(3), "kind": np.array([1.0, 3.0])}
    _, g = net.grads(X, Y, W)
    worst = 0.0
    for k, P in net.p.items():
        for idx in list(np.ndindex(P.shape))[:: max(1, P.size // 15)]:
            old = P[idx]
            P[idx] = old + 1e-6
            lp, _ = net.grads(X, Y, W)
            P[idx] = old - 1e-6
            lm, _ = net.grads(X, Y, W)
            P[idx] = old
            num = (lp - lm) / 2e-6
            worst = max(worst, abs(num - g[k][idx]) / max(1e-6, abs(num) + abs(g[k][idx])))
    assert worst < 1e-4, f"worst relative gradient error {worst:.2e}"


if __name__ == "__main__":
    test_gradients_match_finite_differences()
    print("gradient check passed")
