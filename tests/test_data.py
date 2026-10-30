import pandas as pd
import pytest

from forecast import data


def write(path, text):
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def raw_dir(tmp_path):
    write(
        tmp_path / "air_visit_data.csv",
        "air_store_id,visit_date,visitors\n"
        "air_b,2016-01-02,5\n"
        "air_a,2016-01-02,20\n"
        "air_a,2016-01-01,10\n",
    )
    write(
        tmp_path / "date_info.csv",
        "calendar_date,day_of_week,holiday_flg\n"
        "2016-01-01,Friday,1\n"
        "2016-01-02,Saturday,0\n",
    )
    write(
        tmp_path / "air_store_info.csv",
        "air_store_id,air_genre_name,air_area_name,latitude,longitude\n"
        "air_a,Izakaya,Hyōgo-ken Kōbe-shi Kumoidōri,34.69,135.19\n",
    )
    write(
        tmp_path / "sample_submission.csv",
        "id,visitors\n"
        "air_00a91d42b08b08d9_2017-04-23,0\n"
        "air_00a91d42b08b08d9_2017-04-24,0\n",
    )
    return tmp_path


def test_load_visits_sorted_and_typed(raw_dir):
    df = data.load_visits(raw_dir)
    assert len(df) == 3
    assert pd.api.types.is_datetime64_any_dtype(df["visit_date"])
    assert list(df["air_store_id"]) == ["air_a", "air_a", "air_b"]
    assert df["visit_date"].iloc[0] == pd.Timestamp("2016-01-01")


def test_duplicate_store_date_raises(raw_dir):
    write(
        raw_dir / "air_visit_data.csv",
        "air_store_id,visit_date,visitors\nair_a,2016-01-01,10\nair_a,2016-01-01,12\n",
    )
    with pytest.raises(ValueError, match="duplicate"):
        data.load_visits(raw_dir)


def test_negative_visitors_raises(raw_dir):
    write(
        raw_dir / "air_visit_data.csv",
        "air_store_id,visit_date,visitors\nair_a,2016-01-01,-3\n",
    )
    with pytest.raises(ValueError, match="negative"):
        data.load_visits(raw_dir)


def test_missing_column_raises(raw_dir):
    write(raw_dir / "air_visit_data.csv", "air_store_id,visit_date\nair_a,2016-01-01\n")
    with pytest.raises(ValueError, match="missing columns"):
        data.load_visits(raw_dir)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        data.load_visits(tmp_path)


def test_split_submission_id_uses_last_underscore():
    out = data.split_submission_id(pd.Series(["air_00a91d42b08b08d9_2017-04-23"]))
    assert out["air_store_id"].iloc[0] == "air_00a91d42b08b08d9"
    assert out["visit_date"].iloc[0] == pd.Timestamp("2017-04-23")


def test_load_submission(raw_dir):
    sub = data.load_submission(raw_dir)
    assert list(sub.columns) == ["id", "air_store_id", "visit_date", "visitors"]
    assert len(sub) == 2


def test_store_info_prefecture(raw_dir):
    info = data.load_store_info(raw_dir)
    assert info["prefecture"].iloc[0] == "Hyōgo-ken"


def test_calendar_loads(raw_dir):
    cal = data.load_calendar(raw_dir)
    assert cal["holiday_flg"].tolist() == [1, 0]


REAL = data.DEFAULT_DATA_DIR / "air_visit_data.csv"


@pytest.mark.skipif(not REAL.exists(), reason="raw Kaggle data not available")
def test_real_visits_shape():
    df = data.load_visits()
    assert df.shape == (252108, 3)
    assert df["air_store_id"].nunique() == 829