"""Transparent change-evidence operations used by the case study."""

from __future__ import annotations

import numpy as np


def persistent_mask(
    observations: np.ndarray,
    *,
    threshold: float,
    minimum_observations: int,
) -> np.ndarray:
    """Flag pixels that exceed a threshold often enough to be persistent."""

    values = np.asarray(observations, dtype="float32")
    if values.ndim < 2:
        raise ValueError("observations must have a time axis and spatial axes")
    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    if minimum_observations <= 0:
        raise ValueError("minimum_observations must be positive")
    usable = np.isfinite(values)
    count = np.sum(usable & (values >= threshold), axis=0)
    return count >= minimum_observations


def combine_change_evidence(
    spectral_change: np.ndarray,
    embedding_distance: np.ndarray,
    *,
    spectral_weight: float = 0.55,
    embedding_weight: float = 0.45,
    embedding_scale: float = 0.5,
) -> np.ndarray:
    """Combine two bounded screening signals into a 0–1 review score.

    The result is a *heuristic score*, not a probability.  Calibration requires
    reviewed labels and belongs in the evaluation stage.
    """

    spectral = np.asarray(spectral_change, dtype="float32")
    embedding = np.asarray(embedding_distance, dtype="float32")
    if spectral.shape != embedding.shape:
        raise ValueError("change surfaces must have matching shapes")
    if spectral_weight < 0 or embedding_weight < 0:
        raise ValueError("weights must be non-negative")
    if not np.isclose(spectral_weight + embedding_weight, 1.0):
        raise ValueError("weights must sum to 1")
    if embedding_scale <= 0:
        raise ValueError("embedding_scale must be positive")
    spectral_signal = np.clip(spectral, 0.0, 1.0)
    embedding_signal = np.clip(embedding / embedding_scale, 0.0, 1.0)
    score = spectral_weight * spectral_signal + embedding_weight * embedding_signal
    return np.where(np.isfinite(score), score, np.nan).astype("float32")


def agreement_mask(
    spectral_change: np.ndarray,
    embedding_distance: np.ndarray,
    *,
    spectral_threshold: float = 0.5,
    embedding_threshold: float = 0.25,
) -> np.ndarray:
    """Return pixels where the two evidence streams agree on a binary signal."""

    spectral = np.asarray(spectral_change, dtype="float32")
    embedding = np.asarray(embedding_distance, dtype="float32")
    if spectral.shape != embedding.shape:
        raise ValueError("change surfaces must have matching shapes")
    usable = np.isfinite(spectral) & np.isfinite(embedding)
    same = (spectral >= spectral_threshold) == (embedding >= embedding_threshold)
    return usable & same
