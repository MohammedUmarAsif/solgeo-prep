"""Low-label, model-agnostic embedding utilities for Earth observation."""

from .core import EmbeddingConfig, EmbeddingModel, evaluate, fit_nearest_centroid, spatial_group_split
from .evaluation import EvaluationSummary, evaluate_predictions, spatial_group_indices
from .features import (
    FeatureStandardizer,
    PrototypeClassifier,
    cosine_similarity,
    extract_patches,
    feature_cache_key,
)

__all__ = [
    "FeatureStandardizer",
    "EvaluationSummary",
    "EmbeddingConfig",
    "EmbeddingModel",
    "PrototypeClassifier",
    "cosine_similarity",
    "extract_patches",
    "feature_cache_key",
    "evaluate",
    "evaluate_predictions",
    "fit_nearest_centroid",
    "spatial_group_split",
    "spatial_group_indices",
]
