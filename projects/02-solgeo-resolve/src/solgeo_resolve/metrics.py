"""Spectral fidelity and uncertainty metrics for SR evaluation."""

from __future__ import annotations

import numpy as np


def spectral_angle_map(reference: np.ndarray, estimate: np.ndarray, channel_axis: int = 0) -> np.ndarray:
    """Return per-pixel spectral angle in radians."""
    reference, estimate = _pair(reference, estimate)
    reference = np.moveaxis(reference, channel_axis, -1)
    estimate = np.moveaxis(estimate, channel_axis, -1)
    numerator = np.sum(reference * estimate, axis=-1)
    denominator = np.linalg.norm(reference, axis=-1) * np.linalg.norm(estimate, axis=-1)
    cosine = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator, dtype=np.float32),
        where=denominator > 1e-8,
    )
    return np.arccos(np.clip(cosine, -1.0, 1.0))


def index_preservation(reference: np.ndarray, estimate: np.ndarray, red: int, nir: int) -> float:
    """Return mean absolute error for a normalized-difference index."""
    reference, estimate = _pair(reference, estimate)
    ref_index = _normalized_difference(reference[red], reference[nir])
    est_index = _normalized_difference(estimate[red], estimate[nir])
    return float(np.nanmean(np.abs(ref_index - est_index)))


def ensemble_uncertainty(predictions: np.ndarray, ensemble_axis: int = 0) -> dict[str, np.ndarray | float]:
    """Summarize repeated predictions as mean, standard deviation, and mean uncertainty."""
    predictions = np.asarray(predictions, dtype=np.float32)
    if predictions.ndim < 2 or predictions.shape[ensemble_axis] < 2:
        raise ValueError("predictions need at least two ensemble members")
    mean = predictions.mean(axis=ensemble_axis)
    std = predictions.std(axis=ensemble_axis)
    return {"mean": mean, "std": std, "mean_std": float(std.mean())}


def _normalized_difference(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    denominator = first + second
    return np.divide(
        first - second,
        denominator,
        out=np.full_like(first, np.nan, dtype=np.float32),
        where=np.abs(denominator) > 1e-8,
    )


def _pair(reference: np.ndarray, estimate: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    reference, estimate = np.asarray(reference, dtype=np.float32), np.asarray(estimate, dtype=np.float32)
    if reference.shape != estimate.shape:
        raise ValueError("reference and estimate must have the same shape")
    if reference.ndim < 2:
        raise ValueError("inputs must contain channels and spatial dimensions")
    return reference, estimate
