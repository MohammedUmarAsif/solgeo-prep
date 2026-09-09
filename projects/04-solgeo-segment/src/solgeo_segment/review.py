"""Deterministic proposal masks and explicit human corrections."""

from __future__ import annotations

from typing import Literal

import numpy as np


def threshold_mask(
    image: np.ndarray,
    threshold: float,
    direction: Literal["above", "below"] = "above",
) -> np.ndarray:
    """Create a finite-value proposal mask from a scalar raster."""
    image = np.asarray(image)
    if image.ndim != 2:
        raise ValueError("image must have shape (height, width)")
    if not np.isfinite(threshold):
        raise ValueError("threshold must be finite")
    if direction == "above":
        return np.isfinite(image) & (image >= threshold)
    if direction == "below":
        return np.isfinite(image) & (image <= threshold)
    raise ValueError("direction must be above or below")


def apply_review_edits(
    mask: np.ndarray,
    add: np.ndarray | None = None,
    remove: np.ndarray | None = None,
) -> tuple[np.ndarray, list[dict[str, str]]]:
    """Apply explicit add/remove masks and return an auditable edit log."""
    result = _validate_mask(mask).copy()
    log: list[dict[str, str]] = []
    if add is not None:
        add = _same_shape(add, result)
        result |= add
        log.append({"operation": "add", "pixels": str(int(add.sum()))})
    if remove is not None:
        remove = _same_shape(remove, result)
        result &= ~remove
        log.append({"operation": "remove", "pixels": str(int(remove.sum()))})
    return result, log


def _validate_mask(mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2:
        raise ValueError("mask must have shape (height, width)")
    return mask


def _same_shape(candidate: np.ndarray, reference: np.ndarray) -> np.ndarray:
    candidate = _validate_mask(candidate)
    if candidate.shape != reference.shape:
        raise ValueError("edit masks must have the same shape as mask")
    return candidate
