"""Robust temporal change candidates over a time-by-pixel feature stack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

Direction = Literal["increase", "decrease", "absolute"]


@dataclass(frozen=True)
class ChangeConfig:
    """Controls for baseline, persistence, and valid-data gates."""

    baseline_fraction: float = 0.5
    threshold: float = 3.0
    min_persistence: float = 0.6
    min_valid_fraction: float = 0.75
    direction: Direction = "absolute"

    def __post_init__(self) -> None:
        if not 0 < self.baseline_fraction < 1:
            raise ValueError("baseline_fraction must be between 0 and 1")
        if self.threshold <= 0:
            raise ValueError("threshold must be positive")
        if not 0 < self.min_persistence <= 1:
            raise ValueError("min_persistence must be between 0 and 1")
        if not 0 < self.min_valid_fraction <= 1:
            raise ValueError("min_valid_fraction must be between 0 and 1")
        if self.direction not in {"increase", "decrease", "absolute"}:
            raise ValueError("direction must be increase, decrease, or absolute")


@dataclass(frozen=True)
class ChangeResult:
    """Arrays that make a review candidate explainable."""

    baseline: np.ndarray
    median_change: np.ndarray
    persistence: np.ndarray
    score: np.ndarray
    candidate: np.ndarray
    valid_fraction: np.ndarray
    baseline_scale: np.ndarray
    uncertainty: np.ndarray


def detect_persistent_change(
    observations: np.ndarray,
    config: ChangeConfig | None = None,
) -> ChangeResult:
    """Detect persistent standardized change from ``(time, height, width)`` data."""
    config = config or ChangeConfig()
    observations = _validate_observations(observations)
    time_count = observations.shape[0]
    baseline_end = max(1, int(np.floor(time_count * config.baseline_fraction)))
    if baseline_end >= time_count:
        raise ValueError("observations need at least one post-baseline acquisition")

    baseline_values = observations[:baseline_end]
    post_values = observations[baseline_end:]
    baseline = np.nanmedian(baseline_values, axis=0)
    mad = np.nanmedian(np.abs(baseline_values - baseline[None, ...]), axis=0)
    scale = np.maximum(1.4826 * mad, 1e-6)
    standardized = (post_values - baseline[None, ...]) / scale[None, ...]
    valid = np.isfinite(post_values) & np.isfinite(baseline[None, ...])
    valid_fraction = valid.mean(axis=0)

    if config.direction == "increase":
        signal = standardized
    elif config.direction == "decrease":
        signal = -standardized
    else:
        signal = np.abs(standardized)
    hit = np.where(valid, signal >= config.threshold, False)
    persistence = np.divide(
        hit.sum(axis=0),
        valid.sum(axis=0),
        out=np.zeros_like(baseline, dtype=np.float32),
        where=valid.sum(axis=0) > 0,
    )
    median_change = np.nanmedian(np.where(valid, signal, np.nan), axis=0)
    score = (100 * persistence * np.clip(median_change / config.threshold, 0, 1)).astype(np.float32)
    candidate = (persistence >= config.min_persistence) & (valid_fraction >= config.min_valid_fraction)
    uncertainty = np.clip(0.5 * (1.0 - persistence) + 0.5 * (1.0 - valid_fraction), 0, 1).astype(np.float32)
    return ChangeResult(
        baseline=baseline,
        median_change=median_change,
        persistence=persistence,
        score=score,
        candidate=candidate,
        valid_fraction=valid_fraction.astype(np.float32),
        baseline_scale=scale.astype(np.float32),
        uncertainty=uncertainty,
    )


def _validate_observations(observations: np.ndarray) -> np.ndarray:
    observations = np.asarray(observations, dtype=np.float32)
    if observations.ndim != 3:
        raise ValueError("observations must have shape (time, height, width)")
    if observations.shape[0] < 3:
        raise ValueError("observations need at least three acquisitions")
    if min(observations.shape[1:]) <= 0:
        raise ValueError("spatial dimensions must be positive")
    return observations
