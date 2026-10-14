from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import yaml

from .data import load_or_generate_sample_data, validate_and_clean
from .features import make_model_features
from .train import PROJECT_ROOT, chronological_split



def regression_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }


def evaluate_model(model_path: str | Path, data_path: str | Path, config_path: str | Path = "configs/config.yaml") -> dict:
    def resolve(path: str | Path) -> Path:
        candidate = Path(path)
        return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate

    config = yaml.safe_load(resolve(config_path).read_text(encoding="utf-8"))
    data_cfg = config["data"]
    df = validate_and_clean(
        load_or_generate_sample_data(resolve(data_path)),
        data_cfg["timestamp_column"],
        data_cfg["road_id_column"],
        data_cfg["target_column"],
    )
    feature_df = make_model_features(
        df,
        target_col=data_cfg["target_column"],
        road_col=data_cfg["road_id_column"],
        timestamp_col=data_cfg["timestamp_column"],
    ).dropna(subset=[data_cfg["target_column"]])
    train_df, _, test_df = chronological_split(
        feature_df,
        target_col=data_cfg["target_column"],
        test_fraction=config["training"]["test_fraction"],
        validation_fraction=config["training"]["validation_fraction"],
    )
    artifact = joblib.load(resolve(model_path))
    pipeline = artifact["pipeline"] if isinstance(artifact, dict) else artifact
    feature_columns = artifact.get("feature_columns") if isinstance(artifact, dict) else None
    if feature_columns is None:
        feature_columns = [
            column for column in test_df.columns
            if column not in [data_cfg["target_column"], data_cfg["road_id_column"], data_cfg["timestamp_column"]]
            and pd.api.types.is_numeric_dtype(test_df[column])
        ]
    X_test = test_df.reindex(columns=feature_columns)
    y_test = test_df[data_cfg["target_column"]]
    predictions = pipeline.predict(X_test)
    metrics = regression_metrics(y_test, predictions)
    baseline_value = (
        artifact.get("training_target_median", float(train_df[data_cfg["target_column"]].median()))
        if isinstance(artifact, dict)
        else float(train_df[data_cfg["target_column"]].median())
    )
    baseline_predictions = test_df["lag_1_speed"].fillna(baseline_value).to_numpy()
    metrics["baseline"] = {
        "name": "previous_speed_or_training_median",
        "mae": float(mean_absolute_error(y_test, baseline_predictions)),
        "rmse": float(mean_squared_error(y_test, baseline_predictions) ** 0.5),
    }
    metrics["test_rows"] = int(len(test_df))
    metrics["test_start"] = test_df[data_cfg["timestamp_column"]].min().isoformat()
    metrics["test_end"] = test_df[data_cfg["timestamp_column"]].max().isoformat()
    return metrics


if __name__ == "__main__":
    config = yaml.safe_load((PROJECT_ROOT / "configs/config.yaml").read_text(encoding="utf-8"))
    metrics = evaluate_model(config["data"]["model_path"], config["data"]["input_path"])
    print(json.dumps(metrics, indent=2))
