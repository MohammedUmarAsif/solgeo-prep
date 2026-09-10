import numpy as np
import pytest

from solgeo_prep import (
    annual_cosine_distance,
    combine_change_evidence,
    decode_signed_embeddings,
    encode_demo_embeddings,
    persistent_mask,
)


def test_alphaearth_decode_preserves_nodata_and_round_trips_demo_values():
    original = np.array([[0.25, -0.5, 0.0]], dtype="float32")
    encoded = encode_demo_embeddings(original)
    encoded[0, 2] = -128
    decoded = decode_signed_embeddings(encoded)

    assert decoded.valid.tolist() == [[True, True, False]]
    np.testing.assert_allclose(decoded.values[0, :2], original[0, :2], atol=0.01)
    assert np.isnan(decoded.values[0, 2])


def test_annual_cosine_distance_is_small_for_identical_vectors():
    vectors = np.zeros((2, 2, 64), dtype="float32")
    vectors[..., 0] = 1.0
    encoded = encode_demo_embeddings(vectors)
    distance = annual_cosine_distance(encoded, encoded)

    np.testing.assert_allclose(distance, 0.0, atol=0.01)


def test_persistent_mask_requires_repeated_observations():
    observations = np.array(
        [
            [[0.8, 0.1], [0.8, np.nan]],
            [[0.7, 0.9], [0.1, np.nan]],
            [[0.6, 0.1], [0.1, np.nan]],
        ],
        dtype="float32",
    )

    result = persistent_mask(observations, threshold=0.5, minimum_observations=2)

    assert result.tolist() == [[True, False], [False, False]]


def test_change_fusion_requires_weights_to_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1"):
        combine_change_evidence(np.ones((2, 2)), np.ones((2, 2)), spectral_weight=0.3)
