"""Load and validate the raw Recruit restaurant data."""
from pathlib import Path

import pandas as pd

# <repo root>/data/raw, independent of where the code is run from
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def _path(name, data_dir):
    base = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    path = base / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Put the Kaggle CSV files in {base}")
    return path


def _require_columns(df, columns, name):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: missing columns {missing}")


def validate_visits(df):
    """Fail fast if the visits table breaks a rule we rely on."""
    _require_columns(df, ["air_store_id", "visit_date", "visitors"], "visits")
    if df[["air_store_id", "visit_date", "visitors"]].isna().any().any():
        raise ValueError("visits: contains missing values")
    if (df["visitors"] < 0).any():
        raise ValueError("visits: negative visitors")
    if df.duplicated(["air_store_id", "visit_date"]).any():
        raise ValueError("visits: duplicate (air_store_id, visit_date) rows")
    return df


def load_visits(data_dir=None):
    """One row per store and day, sorted by store and date."""
    df = pd.read_csv(_path("air_visit_data", data_dir), encoding="utf-8")
    _require_columns(df, ["air_store_id", "visit_date", "visitors"], "visits")
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    validate_visits(df)
    return df.sort_values(["air_store_id", "visit_date"]).reset_index(drop=True)


def load_calendar(data_dir=None):
    df = pd.read_csv(_path("date_info", data_dir), encoding="utf-8")
    _require_columns(df, ["calendar_date", "day_of_week", "holiday_flg"], "calendar")
    df["calendar_date"] = pd.to_datetime(df["calendar_date"])
    if df["calendar_date"].duplicated().any():
        raise ValueError("calendar: duplicate dates")
    return df.sort_values("calendar_date").reset_index(drop=True)


def load_store_info(data_dir=None):
    df = pd.read_csv(_path("air_store_info", data_dir), encoding="utf-8")
    _require_columns(
        df,
        ["air_store_id", "air_genre_name", "air_area_name", "latitude", "longitude"],
        "store_info",
    )
    if df["air_store_id"].duplicated().any():
        raise ValueError("store_info: duplicate air_store_id")
    # the first word of the area name is the prefecture, e.g. "Hyōgo-ken"
    df["prefecture"] = df["air_area_name"].str.split().str[0]
    return df


def split_submission_id(ids):
    """'air_00a91d42b08b08d9_2017-04-23' -> store id and date.

    The store id itself contains an underscore, so split on the LAST one.
    """
    parts = ids.str.rsplit("_", n=1)
    return pd.DataFrame(
        {
            "id": ids,
            "air_store_id": parts.str[0],
            "visit_date": pd.to_datetime(parts.str[1]),
        }
    )


def load_submission(data_dir=None):
    df = pd.read_csv(_path("sample_submission", data_dir), encoding="utf-8")
    _require_columns(df, ["id", "visitors"], "submission")
    return split_submission_id(df["id"]).assign(visitors=df["visitors"].to_numpy())