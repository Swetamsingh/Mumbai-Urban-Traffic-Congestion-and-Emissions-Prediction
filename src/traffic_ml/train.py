from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

import yaml

from .data import load_or_generate_sample_data, save_processed_data, validate_and_clean
from .features import make_model_features


ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = ROOT


def chronological_split(df: pd.DataFrame, target_col: str = "traffic_speed_kmh", test_fraction: float = 0.2, validation_fraction: float = 0.15):
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1.")
    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be between 0 and 1.")
    if test_fraction + validation_fraction >= 1:
        raise ValueError("test_fraction and validation_fraction must sum to less than 1.")

    if "timestamp" not in df.columns:
        raise ValueError("Chronological splitting requires a timestamp column.")
    result = df.copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], errors="coerce")
    if result["timestamp"].isna().any():
        raise ValueError("Chronological splitting requires valid timestamps.")
    timestamps = result["timestamp"].drop_duplicates().sort_values().reset_index(drop=True)
    if len(timestamps) < 3:
        raise ValueError("At least three distinct timestamps are required for train/validation/test splits.")

    test_start = max(1, min(len(timestamps) - 1, int(len(timestamps) * (1 - test_fraction))))
    val_start = max(1, min(test_start - 1, int(len(timestamps) * (1 - test_fraction - validation_fraction))))
    validation_time = timestamps.iloc[val_start]
    test_time = timestamps.iloc[test_start]
    train_df = result[result["timestamp"] < validation_time].copy()
    val_df = result[(result["timestamp"] >= validation_time) & (result["timestamp"] < test_time)].copy()
    test_df = result[result["timestamp"] >= test_time].copy()
    return train_df, val_df, test_df


def build_pipeline(random_state: int = 42) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestRegressor(n_estimators=200, random_state=random_state)),
        ]
    )


def _project_path(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else PROJECT_ROOT / value


def train_model(config_path: str | Path = "configs/config.yaml") -> dict:
    config = yaml.safe_load(_project_path(config_path).read_text(encoding="utf-8"))

    data_cfg = config["data"]
    training_cfg = config["training"]

    data_path = _project_path(data_cfg["input_path"])
    processed_path = _project_path(data_cfg["processed_path"])
    model_path = _project_path(data_cfg["model_path"])

    raw_df = load_or_generate_sample_data(data_path)
    cleaned_df = validate_and_clean(raw_df, data_cfg["timestamp_column"], data_cfg["road_id_column"], data_cfg["target_column"])
    save_processed_data(cleaned_df, processed_path)

    feature_df = make_model_features(
        cleaned_df,
        target_col=data_cfg["target_column"],
        road_col=data_cfg["road_id_column"],
        timestamp_col=data_cfg["timestamp_column"],
    )
    feature_df = feature_df.dropna(subset=[data_cfg["target_column"]]).reset_index(drop=True)
    feature_cols = [
        col
        for col in feature_df.columns
        if col not in [data_cfg["target_column"], data_cfg["road_id_column"], data_cfg["timestamp_column"]]
        and pd.api.types.is_numeric_dtype(feature_df[col])
    ]

    train_df, val_df, test_df = chronological_split(
        feature_df,
        target_col=data_cfg["target_column"],
        test_fraction=training_cfg["test_fraction"],
        validation_fraction=training_cfg["validation_fraction"],
    )

    if train_df.empty or val_df.empty or test_df.empty:
        raise ValueError("The configured split produced an empty train, validation, or test set.")
    X_train = train_df[feature_cols]
    y_train = train_df[data_cfg["target_column"]]
    X_test = test_df[feature_cols]
    y_test = test_df[data_cfg["target_column"]]

    pipeline = build_pipeline(training_cfg.get("random_state", 42))
    pipeline.fit(X_train, y_train)

    validation_predictions = pipeline.predict(val_df[feature_cols])
    predictions = pipeline.predict(X_test)
    baseline_predictions = test_df["lag_1_speed"].fillna(y_train.median()).to_numpy()
    test_times = test_df[data_cfg["timestamp_column"]]
    metrics = {
        "model_name": pipeline.named_steps["model"].__class__.__name__,
        "target": data_cfg["target_column"],
        "unit": "km/h",
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(mean_squared_error(y_test, predictions) ** 0.5),
        "r2": float(r2_score(y_test, predictions)),
        "validation": {
            "mae": float(mean_absolute_error(val_df[data_cfg["target_column"]], validation_predictions)),
            "rmse": float(mean_squared_error(val_df[data_cfg["target_column"]], validation_predictions) ** 0.5),
        },
        "baseline": {
            "name": "previous_speed_or_training_median",
            "mae": float(mean_absolute_error(y_test, baseline_predictions)),
            "rmse": float(mean_squared_error(y_test, baseline_predictions) ** 0.5),
        },
        "validation_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "test_start": test_times.min().isoformat(),
        "test_end": test_times.max().isoformat(),
        "feature_columns": feature_cols,
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "feature_columns": feature_cols,
            "target_column": data_cfg["target_column"],
            "road_id_column": data_cfg["road_id_column"],
            "timestamp_column": data_cfg["timestamp_column"],
            "training_target_median": float(y_train.median()),
        },
        model_path,
    )

    metrics_path = _project_path(data_cfg["metrics_path"])
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return metrics


if __name__ == "__main__":
    metrics = train_model()
    print(json.dumps(metrics, indent=2))
