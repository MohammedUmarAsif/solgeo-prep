"""Command-line demonstration for low-label embedding classification."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .core import evaluate, fit_nearest_centroid, spatial_group_split


def main(argv: list[str] | None = None) -> int:
    """Run a deterministic synthetic embedding experiment."""
    parser = argparse.ArgumentParser(prog="solgeo-embed")
    parser.add_argument("--output", type=Path, default=Path("embedding-demo.json"))
    args = parser.parse_args(argv)
    rng = np.random.default_rng(19)
    centers = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]], dtype="float32")
    embeddings = np.concatenate([center + rng.normal(0, 0.08, size=(30, 4)) for center in centers])
    labels = np.repeat(np.array(["built", "vegetation", "water"]), 30)
    groups = np.repeat(np.arange(9), 10)
    train, test = spatial_group_split(labels, groups, test_fraction=1 / 3)
    model = fit_nearest_centroid(embeddings[train], labels[train])
    payload = {
        "evaluation": evaluate(model, embeddings[test], labels[test]),
        "provenance": model.provenance,
    }
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0
