"""The brain's network in PyTorch, loading the weights trained in NumPy, so it can be trained further on a GPU.

    import torch_brain
    net, labels = torch_brain.load("brain/model/brain.npz")
    probs, emb = net(x)            # x: (batch, 8192) TF-IDF features from text.Vectorizer

The layers are exactly those in nn.py: hidden ReLU layers (dropout while training), a tanh embedding, and one
softmax head per task. Train it further with any PyTorch optimiser; save with save(), which writes the same .npz
layout the NumPy tools and the viewer read.
"""
from __future__ import annotations

import json

import numpy as np
import torch
from torch import nn


class BrainNet(nn.Module):
    def __init__(self, n_in: int, hidden: list[int], emb: int, heads: dict[str, int], drop: float = 0.3):
        super().__init__()
        dims = [n_in, *hidden]
        self.hidden = nn.ModuleList(nn.Linear(dims[k], dims[k + 1]) for k in range(len(hidden)))
        self.embed = nn.Linear(dims[-1], emb)
        self.heads = nn.ModuleDict({h: nn.Linear(emb, n) for h, n in heads.items()})
        self.drop = nn.Dropout(drop)

    def forward(self, x: torch.Tensor) -> tuple[dict[str, torch.Tensor], torch.Tensor]:
        for layer in self.hidden:
            x = self.drop(torch.relu(layer(x)))
        e = torch.tanh(self.embed(x))
        return {h: torch.softmax(head(e), dim=-1) for h, head in self.heads.items()}, e

    def logits(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        """Raw scores, for training with nn.CrossEntropyLoss."""
        for layer in self.hidden:
            x = self.drop(torch.relu(layer(x)))
        e = torch.tanh(self.embed(x))
        return {h: head(e) for h, head in self.heads.items()}


def load(path: str) -> tuple[BrainNet, dict[str, list[str]]]:
    """Build the network from a NumPy .npz (NumPy stores weights as (in, out); PyTorch as (out, in))."""
    z = np.load(path, allow_pickle=False)
    labels = json.loads(str(z["labels"]))
    p = {k[2:]: z[k].astype(np.float32) for k in z.files if k.startswith("p_")}
    depth = sum(1 for k in p if k[0] == "W" and k[1:].isdigit())
    hidden = [p[f"W{k + 1}"].shape[1] for k in range(depth)]
    net = BrainNet(p["W1"].shape[0], hidden, p["We"].shape[1], {h: len(v) for h, v in labels.items()})
    with torch.no_grad():
        for k, layer in enumerate(net.hidden, start=1):
            layer.weight.copy_(torch.from_numpy(p[f"W{k}"].T)); layer.bias.copy_(torch.from_numpy(p[f"b{k}"]))
        net.embed.weight.copy_(torch.from_numpy(p["We"].T)); net.embed.bias.copy_(torch.from_numpy(p["be"]))
        for h, head in net.heads.items():
            head.weight.copy_(torch.from_numpy(p[f"W_{h}"].T)); head.bias.copy_(torch.from_numpy(p[f"b_{h}"]))
    net.eval()
    return net, labels


def save(net: BrainNet, src: str, dst: str) -> None:
    """Write the PyTorch weights back into the NumPy .npz layout (other arrays copied from src)."""
    z = dict(np.load(src, allow_pickle=False))
    for k, layer in enumerate(net.hidden, start=1):
        z[f"p_W{k}"] = layer.weight.detach().numpy().T.astype(np.float16); z[f"p_b{k}"] = layer.bias.detach().numpy().astype(np.float16)
    z["p_We"] = net.embed.weight.detach().numpy().T.astype(np.float16); z["p_be"] = net.embed.bias.detach().numpy().astype(np.float16)
    for h, head in net.heads.items():
        z[f"p_W_{h}"] = head.weight.detach().numpy().T.astype(np.float16); z[f"p_b_{h}"] = head.bias.detach().numpy().astype(np.float16)
    np.savez_compressed(dst, **z)
