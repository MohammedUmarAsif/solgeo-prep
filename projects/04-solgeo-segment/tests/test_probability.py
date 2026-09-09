import numpy as np
import pytest

from solgeo_segment import segment_probability


def test_probability_segmentation_returns_uncertainty_and_objects():
    probabilities = np.zeros((5, 5), dtype=np.float32)
    probabilities[1:3, 1:3] = 0.95
    probabilities[3, 3] = 0.52
    result = segment_probability(probabilities, min_area_pixels=2)
    assert len(result.objects) == 1
    assert result.uncertainty[3, 3] > result.uncertainty[1, 1]
    assert result.needs_review[3, 3]


def test_probability_range_is_validated():
    with pytest.raises(ValueError, match="between 0 and 1"):
        segment_probability(np.array([[1.2]], dtype=np.float32))
