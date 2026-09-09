"""A small frozen-embedding head with leakage-aware evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class EmbeddingConfig:
    """Controls the frozen embedding classifier."""

    temperature: float = 0.15
    review_confidence_threshold: float = 0.65

    def __post_init__(self) -> None:
        if self.temperature <= 0:
            raise ValueError("temperature must be positive")
        if not 0 <= self.review_confidence_threshold <= 1:
            raise ValueError("review_confidence_threshold must be in [0, 1]")


@dataclass
class EmbeddingModel:
    """Nearest-centroid model over normalized, frozen embeddings."""

    labels: np.ndarray
    centroids: np.ndarray
    config: EmbeddingConfig
    provenance: dict[str, Any]

    def predict(self, embeddings: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return labels, confidence, and review mask."""
        values = _normalize(np.asarray(embeddings, dtype="float32"))
        if values.ndim != 2 or values.shape[1] != self.centroids.shape[1]:
            raise ValueError("embeddings must be 2D with the trained feature width")
        similarity = values @ self.centroids.T
        logits = similarity / self.config.temperature
        logits -= logits.max(axis=1, keepdims=True)
        probabilities = np.exp(logits)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        winners = probabilities.argmax(axis=1)
        confidence = probabilities[np.arange(values.shape[0]), winners]
        review = confidence < self.config.review_confidence_threshold
        return self.labels[winners], confidence, review


def fit_nearest_centroid(
    embeddings: np.ndarray,
    labels: np.ndarray,
    config: EmbeddingConfig | None = None,
) -> EmbeddingModel:
    """Fit a transparent classifier without changing the foundation encoder."""
    config = config or EmbeddingConfig()
    values = np.asarray(embeddings, dtype="float32")
    target = np.asarray(labels)
    if values.ndim != 2 or target.ndim != 1 or values.shape[0] != target.shape[0]:
        raise ValueError("embeddings must be 2D and labels must align with rows")
    if not np.isfinite(values).all():
        raise ValueError("embeddings must be finite")
    classes = np.unique(target)
    if classes.size < 2:
        raise ValueError("at least two classes are required")
    centroids = np.stack(
        [_normalize(values[target == label].mean(axis=0, keepdims=True))[0] for label in classes]
    )
    return EmbeddingModel(
        labels=classes,
        centroids=centroids,
        config=config,
        provenance={
            "method": "normalized nearest centroid over frozen embeddings",
            "classes": classes.tolist(),
            "encoder_training": "not performed by this package",
        },
    )


def spatial_group_split(
    labels: np.ndarray,
    group_ids: np.ndarray,
    *,
    test_fraction: float = 0.2,
) -> tuple[np.ndarray, np.ndarray]:
    """Split by spatial group so neighboring samples cannot cross the split."""
    target = np.asarray(labels)
    groups = np.asarray(group_ids)
    if target.ndim != 1 or groups.ndim != 1 or target.shape != groups.shape:
        raise ValueError("labels and group_ids must be aligned 1D arrays")
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be in (0, 1)")
    unique_groups = np.unique(groups)
    test_count = max(1, int(np.ceil(unique_groups.size * test_fraction)))
    selected_positions = np.linspace(0, unique_groups.size - 1, test_count).round().astype(int)
    test_groups = set(unique_groups[selected_positions].tolist())
    test_mask = np.array([group in test_groups for group in groups])
    return np.where(~test_mask)[0], np.where(test_mask)[0]


def evaluate(model: EmbeddingModel, embeddings: np.ndarray, labels: np.ndarray) -> dict[str, Any]:
    """Compute accuracy, macro F1, and review rate for labeled samples."""
    predicted, confidence, review = model.predict(embeddings)
    target = np.asarray(labels)
    accuracy = float(np.mean(predicted == target))
    f1_values: list[float] = []
    for label in model.labels:
        true_positive = np.sum((predicted == label) & (target == label))
        false_positive = np.sum((predicted == label) & (target != label))
        false_negative = np.sum((predicted != label) & (target == label))
        precision = true_positive / max(true_positive + false_positive, 1)
        recall = true_positive / max(true_positive + false_negative, 1)
        f1_values.append(2 * precision * recall / max(precision + recall, 1e-9))
    return {
        "accuracy": accuracy,
        "macro_f1": float(np.mean(f1_values)),
        "review_rate": float(review.mean()),
        "mean_confidence": float(confidence.mean()),
        "sample_count": int(target.size),
    }


def _normalize(values: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, 1e-8)
