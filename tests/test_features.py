import pandas as pd

from traffic_ml.features import add_time_features, create_lag_features


def test_time_features_are_created():
    df = pd.DataFrame({"timestamp": ["2024-01-01 08:00:00", "2024-01-01 09:00:00"]})
    features = add_time_features(df)
    assert "hour" in features.columns
    assert "is_weekend" in features.columns
    assert "hour_sin" in features.columns
    assert "hour_cos" in features.columns


def test_lag_features_are_by_road_segment():
    df = pd.DataFrame({
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 01:00:00", "2024-01-01 00:00:00", "2024-01-01 01:00:00"],
        "road_segment_id": ["ROAD_01", "ROAD_01", "ROAD_02", "ROAD_02"],
        "traffic_speed_kmh": [60.0, 55.0, 50.0, 48.0],
    })
    result = create_lag_features(df)
    assert result["lag_1_speed"].isna().sum() == 2
    assert result["rolling_3_speed"].notna().sum() == 2
    assert result["rolling_3_speed"].isna().sum() == 2
