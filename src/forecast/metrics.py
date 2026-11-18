"""Error metrics for the visitor forecasts."""
import numpy as np


def _as_arrays(actual, pred):
    actual = np.asarray(actual, dtype=float)
    pred = np.asarray(pred, dtype=float)
    if actual.shape != pred.shape:
        raise ValueError(
            f"actual and pred must have the same shape, got {actual.shape} and {pred.shape}"
        )
    if actual.size == 0:
        raise ValueError("actual and pred must not be empty")
    return actual, pred


def mae(actual, pred):
    """Mean absolute error, in visitors."""
    actual, pred = _as_arrays(actual, pred)
    return float(np.mean(np.abs(actual - pred)))


def rmse(actual, pred):
    """Root mean squared error, in visitors. Large errors count more than in MAE."""
    actual, pred = _as_arrays(actual, pred)
    return float(np.sqrt(np.mean((actual - pred) ** 2)))


def rmsle(actual, pred):
    """Root mean squared log error, the competition metric.

    Predictions below 0 are clipped to 0: visitors cannot be negative and
    log1p is undefined below -1.
    """
    actual, pred = _as_arrays(actual, pred)
    pred = np.clip(pred, 0, None)
    return float(np.sqrt(np.mean((np.log1p(pred) - np.log1p(actual)) ** 2)))