import pandas as pd
import pytest

from forecast import data, validation


def make_df(days=10):
    dates = pd.date_range("2016-01-01", periods=days)
    return pd.DataFrame(
        {"air_store_id": "air_a", "visit_date": dates, "visitors": range(days)}
    )


def test_last_days_become_validation():
    train, valid, cutoff = validation.time_split(make_df(10), horizon_days=3)
    assert cutoff == pd.Timestamp("2016-01-07")
    assert train["visit_date"].max() == pd.Timestamp("2016-01-07")
    assert valid["visit_date"].min() == pd.Timestamp("2016-01-08")
    assert len(train) == 7
    assert len(valid) == 3


def test_no_date_appears_in_both_sets():
    train, valid, _ = validation.time_split(make_df(30), horizon_days=7)
    assert set(train["visit_date"]).isdisjoint(set(valid["visit_date"]))
    assert train["visit_date"].max() < valid["visit_date"].min()


def test_invalid_inputs_raise():
    with pytest.raises(ValueError, match="at least 1"):
        validation.time_split(make_df(5), horizon_days=0)
    with pytest.raises(ValueError, match="empty"):
        validation.time_split(make_df(5).iloc[0:0])


REAL = data.DEFAULT_DATA_DIR / "air_visit_data.csv"


@pytest.mark.skipif(not REAL.exists(), reason="raw Kaggle data not available")
def test_real_data_validation_window():
    train, valid, cutoff = validation.time_split(data.load_visits())
    assert cutoff == pd.Timestamp("2017-03-14")
    assert valid["visit_date"].nunique() == 39