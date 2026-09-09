"""Leakage-resistant evaluation helpers for low-label spatial ML."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EvaluationSummary:
    """Metrics with an explicit review rate for uncertain predictions."""

    accuracy: float
    macro_f1: float
    review_rate: float


def spatial_group_indices(
    groups: np.ndarray,
    test_fraction: float = 0.2,
) -> tuple[np.ndarray, np.ndarray]:
    """Split samples by spatial group so neighbouring patches do not leak."""
    groups = np.asarray(groups)
    if groups.ndim != 1 or len(groups) == 0:
        raise ValueError("groups must be a non-empty one-dimensional array")
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1")
    unique = np.unique(groups)
    test_count = max(1, int(round(len(unique) * test_fraction)))
    selected = set(unique[:: max(1, len(unique) // test_count)][:test_count].tolist())
    test = np.isin(groups, list(selected))
    if test.all() or (~test).sum() == 0:
        test[np.flatnonzero(test)[-1]] = False
    return np.flatnonzero(~test), np.flatnonzero(test)


def evaluate_predictions(
    truth: np.ndarray,
    prediction: np.ndarray,
    confidence: np.ndarray,
    review_threshold: float = 0.6,
) -> EvaluationSummary:
    """Compute accuracy, macro-F1, and the fraction routed to review."""
    truth = np.asarray(truth)
    prediction = np.asarray(prediction)
    confidence = np.asarray(confidence, dtype=np.float32)
    if truth.ndim != 1 or prediction.shape != truth.shape or confidence.shape != truth.shape:
        raise ValueError("truth, prediction, and confidence must have matching vectors")
    if not 0 <= review_threshold <= 1:
        raise ValueError("review_threshold must be between 0 and 1")
    labels = np.unique(np.concatenate([truth, prediction]))
    f1_scores = []
    for label in labels:
        tp = np.count_nonzero((truth == label) & (prediction == label))
        fp = np.count_nonzero((truth != label) & (prediction == label))
        fn = np.count_nonzero((truth == label) & (prediction != label))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1_scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return EvaluationSummary(
        accuracy=float(np.mean(truth == prediction)),
        macro_f1=float(np.mean(f1_scores)),
        review_rate=float(np.mean(confidence < review_threshold)),
    )
