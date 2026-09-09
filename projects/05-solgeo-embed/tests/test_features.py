import numpy as np
import pytest

from solgeo_embed import FeatureStandardizer, PrototypeClassifier, extract_patches, feature_cache_key


def test_patch_extraction_returns_locations():
    image = np.zeros((2, 8, 8), dtype=np.float32)
    patches, locations = extract_patches(image, patch_size=4, stride=4)
    assert patches.shape == (4, 2, 4, 4)
    assert locations.tolist() == [[0, 0], [0, 4], [4, 0], [4, 4]]


def test_standardizer_and_prototype_classifier():
    features = np.array([[0, 0], [0, 1], [10, 10], [10, 11]], dtype=np.float32)
    scaled = FeatureStandardizer().fit(features).transform(features)
    classifier = PrototypeClassifier().fit(scaled, np.array(["desert", "desert", "urban", "urban"]))
    labels, confidence, margin = classifier.predict(scaled)
    assert labels.tolist() == ["desert", "desert", "urban", "urban"]
    assert np.all(confidence <= 1.01)
    assert np.all(margin >= 0)


def test_cache_keys_are_stable_and_empty_shapes_rejected():
    assert feature_cache_key("item-1", "Clay", "1", 16) == feature_cache_key("item-1", "Clay", "1", 16)
    with pytest.raises(ValueError, match="empty"):
        FeatureStandardizer().fit(np.empty((0, 3)))
