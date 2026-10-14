from __future__ import annotations

import numpy as np
import pandas as pd


def add_time_features(df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
    result = df.copy()
    if timestamp_col not in result.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    timestamp = pd.to_datetime(result[timestamp_col], errors="coerce")
    if timestamp.isna().any():
        raise ValueError("Invalid timestamps found while creating time features.")

    result["hour"] = timestamp.dt.hour
    result["day_of_week"] = timestamp.dt.dayofweek
    result["month"] = timestamp.dt.month
    result["is_weekend"] = (result["day_of_week"] >= 5).astype(int)
    result["is_rush_hour"] = ((result["hour"].between(7, 9)) | (result["hour"].between(16, 18))).astype(int)
    result["hour_sin"] = np.sin(2 * np.pi * result["hour"] / 24)
    result["hour_cos"] = np.cos(2 * np.pi * result["hour"] / 24)
    result["dayofweek_sin"] = np.sin(2 * np.pi * result["day_of_week"] / 7)
    result["dayofweek_cos"] = np.cos(2 * np.pi * result["day_of_week"] / 7)
    return result


def create_lag_features(
    df: pd.DataFrame,
    road_col: str = "road_segment_id",
    target_col: str = "traffic_speed_kmh",
    timestamp_col: str = "timestamp",
    lags: list[int] | None = None,
    windows: list[int] | None = None,
) -> pd.DataFrame:
    required = [road_col, timestamp_col, target_col]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for lag features: {missing}")

    result = df.sort_values([road_col, timestamp_col], kind="mergesort").copy()
    if lags is None:
        lags = [1, 2, 3]
    if windows is None:
        windows = [3, 6]

    for lag in lags:
        result[f"lag_{lag}_speed"] = result.groupby(road_col)[target_col].transform(lambda s: s.shift(lag))
    for window in windows:
        result[f"rolling_{window}_speed"] = (
            result.groupby(road_col)[target_col].transform(lambda s: s.shift(1).rolling(window, min_periods=1).mean())
        )
    return result


def make_model_features(
    df: pd.DataFrame,
    target_col: str = "traffic_speed_kmh",
    road_col: str = "road_segment_id",
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    result = df.copy()
    if target_col not in result.columns:
        result[target_col] = np.nan
    result = add_time_features(result, timestamp_col=timestamp_col)
    if target_col not in result.columns:
        result[target_col] = np.nan
    result = create_lag_features(
        result,
        road_col=road_col,
        target_col=target_col,
        timestamp_col=timestamp_col,
    )
    candidate_columns = [
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "is_rush_hour",
        "hour_sin",
        "hour_cos",
        "dayofweek_sin",
        "dayofweek_cos",
        "lag_1_speed",
        "lag_2_speed",
        "lag_3_speed",
        "rolling_3_speed",
        "rolling_6_speed",
        "traffic_volume",
        "temperature_c",
        "rainfall_mm",
    ]
    feature_columns = [col for col in candidate_columns if col in result.columns]
    return result[feature_columns + [target_col, road_col, timestamp_col]]


def classify_congestion(speed_kmh: float | int, low_max: float = 30, moderate_min: float = 15) -> str:
    if speed_kmh <= moderate_min:
        return "Severe"
    if speed_kmh <= low_max:
        return "High"
    if speed_kmh < 45:
        return "Moderate"
    return "Low"
