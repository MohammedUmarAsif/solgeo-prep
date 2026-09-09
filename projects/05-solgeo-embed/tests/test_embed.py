import numpy as np
import pytest

from solgeo_embed import fit_nearest_centroid, spatial_group_split


def test_nearest_centroid_classifies_separable_embeddings():
    embeddings = np.array([[1, 0], [0.9, 0.1], [0, 1], [0.1, 0.9]], dtype="float32")
    labels = np.array(["urban", "urban", "water", "water"])
    model = fit_nearest_centroid(embeddings, labels)
    predicted, confidence, review = model.predict(np.array([[1, 0], [0, 1]], dtype="float32"))
    assert predicted.tolist() == ["urban", "water"]
    assert np.all(confidence > 0.5)
    assert not review.any()


def test_groups_do_not_cross_train_test_split():
    labels = np.array([0, 0, 1, 1, 0, 1])
    groups = np.array([1, 1, 2, 2, 3, 3])
    train, test = spatial_group_split(labels, groups, test_fraction=1 / 3)
    assert set(groups[train]).isdisjoint(set(groups[test]))


def test_invalid_training_inputs_are_rejected():
    with pytest.raises(ValueError, match="two classes"):
        fit_nearest_centroid(np.ones((3, 2)), np.array([1, 1, 1]))
