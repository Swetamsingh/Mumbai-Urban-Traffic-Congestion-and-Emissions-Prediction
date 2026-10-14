from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["timestamp", "road_segment_id", "traffic_speed_kmh"]


def generate_sample_data(output_path: str | Path | None = None) -> pd.DataFrame:
    """Create a simple synthetic traffic dataset for demo and testing."""
    rng = np.random.default_rng(42)
    start = pd.Timestamp("2024-01-01 00:00:00")
    rows = []
    for road in ["ROAD_01", "ROAD_02", "ROAD_03"]:
        for hour in range(24 * 14):
            timestamp = start + pd.Timedelta(hours=hour)
            base = 50 if road == "ROAD_01" else 45 if road == "ROAD_02" else 60
            hourly_pattern = 18 * np.sin((timestamp.hour / 24) * 2 * np.pi) + 12 * np.cos((timestamp.dayofweek / 7) * 2 * np.pi)
            noise = rng.normal(0, 6)
            speed = max(5, base + hourly_pattern + noise)
            volume = int(max(100, 700 + (50 - speed) * 8 + rng.normal(0, 80)))
            temp = 21 + 8 * np.sin((hour / 24) * 2 * np.pi) + rng.normal(0, 3)
            rain = max(0, 2 + rng.normal(0, 2)) if timestamp.hour in {12, 13, 18, 19} else 0
            road_type = "highway" if road in {"ROAD_01", "ROAD_02"} else "arterial"
            rows.append(
                {
                    "timestamp": timestamp,
                    "road_segment_id": road,
                    "traffic_speed_kmh": round(float(speed), 2),
                    "traffic_volume": int(volume),
                    "temperature_c": round(float(temp), 2),
                    "rainfall_mm": round(float(rain), 2),
                    "road_type": road_type,
                }
            )
    df = pd.DataFrame(rows)
    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
    return df


def load_or_generate_sample_data(path: str | Path) -> pd.DataFrame:
    """Load an existing dataset or generate a sample one when absent."""
    data_path = Path(path)
    if not data_path.exists():
        return generate_sample_data(data_path)
    return pd.read_csv(data_path)


def validate_and_clean(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    road_col: str = "road_segment_id",
    target_col: str = "traffic_speed_kmh",
) -> pd.DataFrame:
    """Validate required columns and clean the dataset."""
    missing = [col for col in [timestamp_col, road_col, target_col] if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    result = df.copy()
    result[timestamp_col] = pd.to_datetime(result[timestamp_col], errors="coerce", format="mixed")
    if result[timestamp_col].isna().any():
        invalid_count = int(result[timestamp_col].isna().sum())
        raise ValueError(f"Encountered {invalid_count} invalid timestamp values.")

    result[road_col] = result[road_col].astype(str)
    numeric_columns = [target_col] + [
        c for c in ["traffic_volume", "temperature_c", "rainfall_mm"] if c in result.columns
    ]
    for col in numeric_columns:
        result[col] = pd.to_numeric(result[col], errors="coerce")
        result[col] = result[col].replace([np.inf, -np.inf], np.nan)

    if (result[target_col].dropna() < 0).any():
        raise ValueError(f"Column {target_col!r} cannot contain negative speeds.")
    for col in ["traffic_volume", "rainfall_mm"]:
        if col in result.columns and (result[col].dropna() < 0).any():
            raise ValueError(f"Column {col!r} cannot contain negative values.")

    result = result.drop_duplicates(subset=[road_col, timestamp_col], keep="first")
    result = result.sort_values([road_col, timestamp_col], kind="mergesort").reset_index(drop=True)
    return result


def save_processed_data(df: pd.DataFrame, output_path: str | Path) -> pd.DataFrame:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return df


def prepare_dataset(path: str | Path, output_path: str | Path | None = None) -> pd.DataFrame:
    df = load_or_generate_sample_data(path)
    cleaned = validate_and_clean(df)
    if output_path is not None:
        save_processed_data(cleaned, output_path)
    return cleaned
