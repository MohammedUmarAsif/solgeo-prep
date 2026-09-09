import numpy as np
import pytest

from solgeo_change import ChangeConfig, detect_persistent_change


def test_persistent_decrease_is_flagged_but_one_off_change_is_not():
    observations = np.ones((8, 4, 4), dtype=np.float32)
    observations[4:, 1, 2] = -3
    observations[4, 2, 3] = -3
    result = detect_persistent_change(
        observations,
        ChangeConfig(direction="decrease", threshold=2, min_persistence=0.75),
    )
    assert result.candidate[1, 2]
    assert not result.candidate[2, 3]
    assert result.score[1, 2] > result.score[0, 0]


def test_missing_observations_are_gated():
    observations = np.ones((8, 3, 3), dtype=np.float32)
    observations[4:, 0, 0] = -3
    observations[5:, 0, 0] = np.nan
    result = detect_persistent_change(
        observations,
        ChangeConfig(direction="decrease", threshold=2, min_valid_fraction=0.75),
    )
    assert result.valid_fraction[0, 0] < 0.75
    assert not result.candidate[0, 0]


def test_config_and_shape_validation():
    with pytest.raises(ValueError, match="direction"):
        ChangeConfig(direction="unknown")
    with pytest.raises(ValueError, match="three acquisitions"):
        detect_persistent_change(np.ones((2, 4, 4)))
