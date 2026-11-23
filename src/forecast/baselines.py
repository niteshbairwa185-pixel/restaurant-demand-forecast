"""Simple baseline forecasts.

Each function takes the training rows and the validation rows and returns
one prediction (in visitors) per row of `valid`, in the same order.
The forecast origin is the last training date (the cutoff).
"""
import numpy as np
import pandas as pd


def global_median(train, valid):
    """The same number for every row: the median of all training visitors."""
    return np.full(len(valid), train["visitors"].median())


def naive_last_value(train, valid):
    """Each store's most recent training value, repeated for every validation day."""
    last = train.sort_values("visit_date").groupby("air_store_id")["visitors"].last()
    pred = valid["air_store_id"].map(last)
    return pred.fillna(train["visitors"].median()).to_numpy()


def store_median(train, valid):
    """Each store's own median; stores without history get the global median."""
    per_store = train.groupby("air_store_id")["visitors"].median()
    pred = valid["air_store_id"].map(per_store)
    return pred.fillna(train["visitors"].median()).to_numpy()


def store_log_mean(train, valid):
    """Each store's average on the log scale, converted back to visitors.

    On the log scale this is the best single number per store for RMSLE.
    """
    log_visitors = np.log1p(train["visitors"])
    per_store = np.expm1(log_visitors.groupby(train["air_store_id"]).mean())
    pred = valid["air_store_id"].map(per_store)
    return pred.fillna(np.expm1(log_visitors.mean())).to_numpy()


def store_weekday_log_mean(train, valid):
    """Like store_log_mean, but separately for each weekday of each store.

    Store and weekday pairs without history fall back to the store-level value.
    """
    history = pd.DataFrame(
        {
            "air_store_id": train["air_store_id"].to_numpy(),
            "weekday": train["visit_date"].dt.dayofweek.to_numpy(),
            "log_visitors": np.log1p(train["visitors"]).to_numpy(),
        }
    )
    table = (
        history.groupby(["air_store_id", "weekday"])["log_visitors"]
        .mean()
        .rename("log_pred")
        .reset_index()
    )
    rows = pd.DataFrame(
        {
            "air_store_id": valid["air_store_id"].to_numpy(),
            "weekday": valid["visit_date"].dt.dayofweek.to_numpy(),
        }
    )
    merged = rows.merge(table, on=["air_store_id", "weekday"], how="left")
    pred = np.expm1(merged["log_pred"].to_numpy())
    return np.where(np.isnan(pred), store_log_mean(train, valid), pred)


def _weeks_back(train, valid):
    """How many whole weeks to go back from each validation day to reach
    the latest date with the same weekday that is not after the cutoff."""
    cutoff = train["visit_date"].max()
    days_ahead = (valid["visit_date"] - cutoff).dt.days.to_numpy()
    return np.ceil(days_ahead / 7).astype(int)


def _lookup(train, valid, weeks_back):
    """Visitors of the same store `weeks_back` weeks before each validation day.

    NaN where the store has no row on that date.
    """
    series = train.set_index(["air_store_id", "visit_date"])["visitors"]
    source = valid["visit_date"].to_numpy() - pd.to_timedelta(7 * weeks_back, unit="D").to_numpy()
    keys = pd.MultiIndex.from_arrays([valid["air_store_id"].to_numpy(), source])
    return series.reindex(keys).to_numpy()


def seasonal_naive(train, valid):
    """The value from the last observed day with the same weekday.

    The forecast origin is the cutoff, so for a day 20 days after the cutoff
    this goes back 3 weeks (a day inside the validation window is not known).
    """
    pred = _lookup(train, valid, _weeks_back(train, valid)).astype(float)
    return np.where(np.isnan(pred), store_weekday_log_mean(train, valid), pred)


def last_same_weekdays_mean(train, valid, k=4):
    """Average, on the log scale, of the last k same weekdays before the cutoff."""
    first = _weeks_back(train, valid)
    columns = [np.log1p(_lookup(train, valid, first + j).astype(float)) for j in range(k)]
    mean_log = pd.DataFrame(np.column_stack(columns)).mean(axis=1).to_numpy()
    pred = np.expm1(mean_log)
    return np.where(np.isnan(pred), store_weekday_log_mean(train, valid), pred)