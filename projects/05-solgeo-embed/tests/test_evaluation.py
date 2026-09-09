import numpy as np

from solgeo_embed import evaluate_predictions, spatial_group_indices


def test_spatial_split_keeps_groups_disjoint():
    groups = np.repeat(np.arange(5), 2)
    train, test = spatial_group_indices(groups, test_fraction=0.4)
    assert set(groups[train]).isdisjoint(set(groups[test]))


def test_evaluation_reports_review_rate():
    summary = evaluate_predictions(
        np.array(["urban", "water", "urban"]),
        np.array(["urban", "urban", "urban"]),
        np.array([0.9, 0.4, 0.8]),
    )
    assert summary.accuracy == 2 / 3
    assert summary.review_rate == 1 / 3
