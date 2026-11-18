"""Time-based split of the visits table."""
import pandas as pd

HORIZON_DAYS = 39


def time_split(df, horizon_days=HORIZON_DAYS, date_col="visit_date"):
    """Split into train and validation; validation is the last `horizon_days` days.

    Returns (train, valid, cutoff), where cutoff is the last training date.
    """
    if horizon_days < 1:
        raise ValueError("horizon_days must be at least 1")
    if df.empty:
        raise ValueError("df is empty")
    last = df[date_col].max()
    cutoff = last - pd.Timedelta(days=horizon_days)
    train = df[df[date_col] <= cutoff]
    valid = df[df[date_col] > cutoff]
    return train, valid, cutoff
