import numpy as np
import pytest

from solgeo_segment import apply_review_edits, objects_from_mask, threshold_mask


def test_threshold_and_components_create_review_objects():
    image = np.zeros((6, 7), dtype=np.float32)
    image[1:3, 1:3] = 5
    image[4, 5] = 5
    mask = threshold_mask(image, 4)
    objects = objects_from_mask(mask, min_area_pixels=2, connectivity=4)
    assert len(objects) == 1
    assert objects[0].area_pixels == 4
    assert objects[0].bbox == (1, 3, 1, 3)


def test_review_edits_are_applied_and_logged():
    mask = np.zeros((3, 3), dtype=bool)
    add = np.zeros_like(mask)
    add[1, 1] = True
    remove = np.zeros_like(mask)
    edited, log = apply_review_edits(mask, add=add, remove=remove)
    assert edited[1, 1]
    assert [entry["operation"] for entry in log] == ["add", "remove"]


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError, match="connectivity"):
        objects_from_mask(np.ones((2, 2), dtype=bool), connectivity=6)
    with pytest.raises(ValueError, match="same shape"):
        apply_review_edits(np.zeros((2, 2), dtype=bool), add=np.zeros((3, 3), dtype=bool))
