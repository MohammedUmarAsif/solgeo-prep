"""Uncertainty-aware conversion of model probability maps into review objects."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .objects import SegmentObject, objects_from_mask


@dataclass(frozen=True)
class ProbabilitySegmentation:
    """A proposal mask plus pixel uncertainty and review objects."""

    probability: np.ndarray
    mask: np.ndarray
    uncertainty: np.ndarray
    objects: tuple[SegmentObject, ...]
    needs_review: np.ndarray


def segment_probability(
    probability: np.ndarray,
    threshold: float = 0.5,
    uncertainty_band: float = 0.15,
    min_area_pixels: int = 1,
    connectivity: int = 8,
) -> ProbabilitySegmentation:
    """Create human-reviewable objects from a calibrated probability raster."""
    probability = np.asarray(probability, dtype=np.float32)
    if probability.ndim != 2:
        raise ValueError("probability must have shape (height, width)")
    if not np.isfinite(probability).all() or np.any((probability < 0) | (probability > 1)):
        raise ValueError("probability must be finite and between 0 and 1")
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1")
    if not 0 < uncertainty_band < 0.5:
        raise ValueError("uncertainty_band must be between 0 and 0.5")
    mask = probability >= threshold
    uncertainty = (1.0 - 2.0 * np.abs(probability - threshold)).clip(0, 1)
    needs_review = np.abs(probability - threshold) <= uncertainty_band
    objects = tuple(objects_from_mask(mask, min_area_pixels=min_area_pixels, connectivity=connectivity))
    return ProbabilitySegmentation(probability, mask, uncertainty, objects, needs_review)
