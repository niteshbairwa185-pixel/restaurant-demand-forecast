import numpy as np
import pandas as pd

from forecast import baselines


def make_train():
    # 14 days starting on a Monday (2016-01-04), so the cutoff is Sunday 2016-01-17
    # store a: 10 visitors on weekdays, 30 on weekends; store b: always 100
    rows = []
    for day in pd.date_range("2016-01-04", periods=14):
        rows.append(("air_a", day, 10 if day.dayofweek < 5 else 30))
        rows.append(("air_b", day, 100))
    return pd.DataFrame(rows, columns=["air_store_id", "visit_date", "visitors"])


def make_valid():
    # a Monday and a Saturday for store a, a Monday for store b,
    # and a Monday for a store that never appears in the training rows
    return pd.DataFrame(
        {
            "air_store_id": ["air_a", "air_a", "air_b", "air_new"],
            "visit_date": pd.to_datetime(
                ["2016-01-18", "2016-01-23", "2016-01-18", "2016-01-18"]
            ),
            "visitors": [0, 0, 0, 0],
        }
    )


def test_global_median_is_one_number_for_every_row():
    pred = baselines.global_median(make_train(), make_valid())
    assert list(pred) == [65, 65, 65, 65]


def test_naive_repeats_the_last_training_value():
    pred = baselines.naive_last_value(make_train(), make_valid())
    assert list(pred) == [30, 30, 100, 65]


def test_store_median_uses_each_store_and_falls_back_for_new_stores():
    pred = baselines.store_median(make_train(), make_valid())
    assert list(pred) == [10, 10, 100, 65]


def test_store_log_mean_lies_between_the_store_values():
    pred = baselines.store_log_mean(make_train(), make_valid())
    assert 10 < pred[0] < 30 and pred[0] == pred[1]
    assert abs(pred[2] - 100) < 1e-9
    assert not np.isnan(pred[3])


def test_weekday_version_separates_weekdays_from_weekends():
    pred = baselines.store_weekday_log_mean(make_train(), make_valid())
    assert abs(pred[0] - 10) < 1e-9
    assert abs(pred[1] - 30) < 1e-9
    assert abs(pred[2] - 100) < 1e-9
    assert not np.isnan(pred[3])


def test_seasonal_naive_copies_the_same_weekday_of_the_last_week():
    pred = baselines.seasonal_naive(make_train(), make_valid())
    assert list(pred[:3]) == [10, 30, 100]
    assert not np.isnan(pred[3])


def test_seasonal_naive_is_anchored_at_the_cutoff():
    # 2016-01-25 is a Monday 8 days after the cutoff: the Monday of 2016-01-18
    # is not known, so the forecast must come from Monday 2016-01-11
    train = make_train()
    train.loc[(train["air_store_id"] == "air_a") & (train["visit_date"] == "2016-01-11"), "visitors"] = 77
    valid = pd.DataFrame(
        {"air_store_id": ["air_a"], "visit_date": pd.to_datetime(["2016-01-25"]), "visitors": [0]}
    )
    assert list(baselines.seasonal_naive(train, valid)) == [77]


def test_seasonal_naive_falls_back_when_the_source_day_is_missing():
    train = make_train()
    train = train[~((train["air_store_id"] == "air_a") & (train["visit_date"] == "2016-01-11"))]
    valid = pd.DataFrame(
        {"air_store_id": ["air_a"], "visit_date": pd.to_datetime(["2016-01-18"]), "visitors": [0]}
    )
    pred = baselines.seasonal_naive(train, valid)
    assert abs(pred[0] - 10) < 1e-9


def test_last_same_weekdays_mean_averages_on_the_log_scale():
    # store c: Mondays 2016-01-04 and 2016-01-11 had 20 and 80 visitors
    train = pd.DataFrame(
        {
            "air_store_id": ["air_c", "air_c", "air_c"],
            "visit_date": pd.to_datetime(["2016-01-04", "2016-01-11", "2016-01-17"]),
            "visitors": [20, 80, 5],
        }
    )
    valid = pd.DataFrame(
        {"air_store_id": ["air_c"], "visit_date": pd.to_datetime(["2016-01-18"]), "visitors": [0]}
    )
    pred = baselines.last_same_weekdays_mean(train, valid, k=2)
    assert 20 < pred[0] < 50        # between the two values, below their plain average


def test_every_baseline_returns_one_prediction_per_valid_row():
    train, valid = make_train(), make_valid()
    for predict in (
        baselines.global_median,
        baselines.naive_last_value,
        baselines.store_median,
        baselines.store_log_mean,
        baselines.store_weekday_log_mean,
        baselines.seasonal_naive,
        baselines.last_same_weekdays_mean,
    ):
        assert len(predict(train, valid)) == len(valid)