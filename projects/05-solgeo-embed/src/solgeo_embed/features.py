"""Deterministic patch, feature, and prototype-classifier primitives."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


def extract_patches(
    image: np.ndarray,
    patch_size: int = 16,
    stride: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract complete ``(channels, patch_height, patch_width)`` patches."""
    image = np.asarray(image)
    if image.ndim != 3:
        raise ValueError("image must have shape (channels, height, width)")
    if patch_size <= 0:
        raise ValueError("patch_size must be positive")
    stride = patch_size if stride is None else stride
    if stride <= 0:
        raise ValueError("stride must be positive")
    _, height, width = image.shape
    patches: list[np.ndarray] = []
    locations: list[tuple[int, int]] = []
    for y in range(0, height - patch_size + 1, stride):
        for x in range(0, width - patch_size + 1, stride):
            patches.append(image[:, y : y + patch_size, x : x + patch_size])
            locations.append((y, x))
    if not patches:
        raise ValueError("image is smaller than patch_size")
    return np.stack(patches), np.asarray(locations, dtype=np.int32)


@dataclass
class FeatureStandardizer:
    """Training-fitted, NaN-safe feature standardization."""

    mean: np.ndarray | None = None
    scale: np.ndarray | None = None

    def fit(self, features: np.ndarray) -> FeatureStandardizer:
        features = _features(features)
        self.mean = np.nanmean(features, axis=0)
        self.scale = np.maximum(np.nanstd(features, axis=0), 1e-6)
        return self

    def transform(self, features: np.ndarray) -> np.ndarray:
        features = _features(features)
        if self.mean is None or self.scale is None:
            raise RuntimeError("fit must be called before transform")
        if features.shape[1] != len(self.mean):
            raise ValueError("feature dimension does not match fitted standardizer")
        return np.nan_to_num((features - self.mean) / self.scale, nan=0.0).astype(np.float32)


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return pairwise cosine similarity between row-wise feature matrices."""
    left, right = _features(left), _features(right)
    if left.shape[1] != right.shape[1]:
        raise ValueError("feature dimensions must match")
    numerator = left @ right.T
    denominator = np.linalg.norm(left, axis=1)[:, None] * np.linalg.norm(right, axis=1)[None, :]
    return np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 1e-8)


@dataclass
class PrototypeClassifier:
    """Centroid classifier with a confidence margin between top classes."""

    labels: np.ndarray | None = None
    prototypes: np.ndarray | None = None

    def fit(self, features: np.ndarray, labels: np.ndarray) -> PrototypeClassifier:
        features = _features(features)
        labels = np.asarray(labels)
        if labels.ndim != 1 or len(labels) != len(features):
            raise ValueError("labels must be one value per feature row")
        unique = np.unique(labels)
        self.labels = unique
        self.prototypes = np.stack([features[labels == label].mean(axis=0) for label in unique])
        return self

    def predict(self, features: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if self.labels is None or self.prototypes is None:
            raise RuntimeError("fit must be called before predict")
        similarities = cosine_similarity(_features(features), self.prototypes)
        order = np.argsort(similarities, axis=1)[:, ::-1]
        best = order[:, 0]
        second = order[:, 1] if len(self.labels) > 1 else best
        best_scores = similarities[np.arange(len(best)), best]
        second_scores = similarities[np.arange(len(best)), second]
        return self.labels[best], best_scores, best_scores - second_scores


def feature_cache_key(source_id: str, model_name: str, model_version: str, patch_size: int) -> str:
    """Return a stable short key for a cached embedding artifact."""
    payload = f"{source_id}|{model_name}|{model_version}|{patch_size}".encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def _features(features: np.ndarray) -> np.ndarray:
    features = np.asarray(features, dtype=np.float32)
    if features.ndim != 2:
        raise ValueError("features must have shape (samples, dimensions)")
    if features.shape[0] == 0 or features.shape[1] == 0:
        raise ValueError("features cannot be empty")
    return features
