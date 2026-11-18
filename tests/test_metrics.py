import numpy as np
import pytest

from forecast import metrics


def test_mae_and_rmse_on_a_known_example():
    assert metrics.mae([10, 100], [20, 50]) == 30
    assert abs(metrics.rmse([10, 100], [20, 50]) - 36.0555) < 1e-3


def test_rmsle_matches_the_hand_calculation():
    assert abs(metrics.rmsle([10, 100], [20, 50]) - 0.665) < 1e-3


def test_perfect_prediction_gives_zero():
    assert metrics.mae([5, 8], [5, 8]) == 0
    assert metrics.rmsle([5, 8], [5, 8]) == 0


def test_negative_prediction_is_clipped_not_nan():
    assert not np.isnan(metrics.rmsle([5, 5], [-2, 5]))


def test_same_ratio_error_is_similar_in_rmsle_but_not_in_mae():
    assert abs(metrics.rmsle([10], [20]) - metrics.rmsle([100], [200])) < 0.1
    assert metrics.mae([100], [200]) == 10 * metrics.mae([10], [20])


def test_shape_mismatch_and_empty_input_raise():
    with pytest.raises(ValueError, match="same shape"):
        metrics.mae([1, 2, 3], [1, 2])
    with pytest.raises(ValueError, match="empty"):
        metrics.rmsle([], [])