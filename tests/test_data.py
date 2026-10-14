import pandas as pd
import pytest

from traffic_ml.data import validate_and_clean


def test_missing_required_columns():
    df = pd.DataFrame({"timestamp": ["2024-01-01 00:00:00"], "road_segment_id": ["ROAD_01"]})
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_and_clean(df)


def test_invalid_timestamp_raises():
    df = pd.DataFrame({
        "timestamp": ["bad-date", "2024-01-01 00:00:00"],
        "road_segment_id": ["ROAD_01", "ROAD_02"],
        "traffic_speed_kmh": [50.0, 60.0],
    })
    with pytest.raises(ValueError, match="invalid timestamp"):
        validate_and_clean(df)


def test_duplicate_rows_are_removed():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 00:00:00"],
        "road_segment_id": ["ROAD_01", "ROAD_01"],
        "traffic_speed_kmh": [50.0, 50.0],
    })
    cleaned = validate_and_clean(df)
    assert len(cleaned) == 1


def test_missing_targets_are_not_fabricated():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 01:00:00"],
        "road_segment_id": ["ROAD_01", "ROAD_01"],
        "traffic_speed_kmh": [50.0, None],
    })
    cleaned = validate_and_clean(df)
    assert cleaned["traffic_speed_kmh"].isna().sum() == 1
