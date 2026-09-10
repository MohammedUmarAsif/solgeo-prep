"""Small, explicit helpers for working with AlphaEarth-style embeddings.

The public AlphaEarth COGs store each embedding component as a signed byte.
The byte is not the final feature value, so decoding must happen before
averaging or comparing vectors.  Keeping this rule in a tiny module makes it
easy to test and easy to reuse in a different study area.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

NODATA_VALUE = -128
EMBEDDING_DIMENSIONS = 64


@dataclass(frozen=True)
class DecodedEmbedding:
    """Decoded values and a mask of pixels with usable embeddings."""

    values: np.ndarray
    valid: np.ndarray


def decode_signed_embeddings(encoded: np.ndarray) -> DecodedEmbedding:
    """Decode signed-byte AlphaEarth values using the published transform.

    Parameters
    ----------
    encoded:
        An array whose final axis contains embedding dimensions.  ``-128`` is
        treated as nodata and is never converted into a real feature value.
    """

    values = np.asarray(encoded)
    if values.ndim < 1:
        raise ValueError("encoded embeddings must have at least one dimension")

    valid = values != NODATA_VALUE
    numeric = values.astype("float32", copy=False)
    magnitude = np.square(numeric / 127.5, dtype="float32")
    decoded = np.sign(numeric) * magnitude
    decoded = np.where(valid, decoded, np.nan).astype("float32")
    return DecodedEmbedding(values=decoded, valid=valid)


def normalize_embeddings(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Normalize vectors along their final axis and return a valid-row mask."""

    array = np.asarray(values, dtype="float32")
    if array.ndim < 1:
        raise ValueError("embeddings must have at least one dimension")
    finite = np.isfinite(array).all(axis=-1)
    norms = np.linalg.norm(np.where(np.isfinite(array), array, 0.0), axis=-1)
    valid = finite & (norms > 1e-8)
    normalized = np.full_like(array, np.nan, dtype="float32")
    normalized[valid] = array[valid] / norms[valid, None]
    return normalized, valid


def cosine_distance(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Return ``1 - cosine similarity`` for matching vector arrays."""

    first_array = np.asarray(first)
    second_array = np.asarray(second)
    if first_array.shape != second_array.shape:
        raise ValueError("embedding arrays must have matching shapes")
    first_normalized, first_valid = normalize_embeddings(first_array)
    second_normalized, second_valid = normalize_embeddings(second_array)
    valid = first_valid & second_valid
    distance = np.full(first_array.shape[:-1], np.nan, dtype="float32")
    similarity = np.sum(first_normalized * second_normalized, axis=-1)
    distance[valid] = 1.0 - np.clip(similarity[valid], -1.0, 1.0)
    return distance


def annual_cosine_distance(
    baseline_encoded: np.ndarray,
    comparison_encoded: np.ndarray,
) -> np.ndarray:
    """Decode two annual products, then compare their normalized vectors."""

    baseline = decode_signed_embeddings(baseline_encoded)
    comparison = decode_signed_embeddings(comparison_encoded)
    if baseline.values.shape != comparison.values.shape:
        raise ValueError("annual embedding arrays must have matching shapes")
    return cosine_distance(baseline.values, comparison.values)


def encode_demo_embeddings(values: np.ndarray) -> np.ndarray:
    """Encode floating-point vectors for the deterministic learning fixture.

    This is deliberately labelled a demo helper.  It is useful for teaching
    the round trip and for tests; production code reads the official COGs.
    """

    array = np.asarray(values, dtype="float32")
    if array.ndim < 1:
        raise ValueError("values must have at least one dimension")
    clipped = np.clip(array, -1.0, 1.0)
    encoded = np.sign(clipped) * np.sqrt(np.abs(clipped)) * 127.5
    return np.clip(np.rint(encoded), -127, 127).astype("int8")
