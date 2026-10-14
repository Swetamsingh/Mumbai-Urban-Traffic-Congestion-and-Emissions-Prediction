from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .features import classify_congestion, make_model_features


def predict_traffic(
    model_path: str | Path,
    df: pd.DataFrame,
    target_col: str = "traffic_speed_kmh",
    history: pd.DataFrame | None = None,
) -> pd.DataFrame:
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model not found at {model_path}")
    if df.empty:
        raise ValueError("At least one prediction row is required.")

    artifact = joblib.load(model_path)
    if isinstance(artifact, dict):
        pipeline = artifact["pipeline"]
        feature_columns = artifact["feature_columns"]
        target_col = artifact.get("target_column", target_col)
        road_col = artifact.get("road_id_column", "road_segment_id")
        timestamp_col = artifact.get("timestamp_column", "timestamp")
    else:
        pipeline = artifact
        feature_columns = None
        road_col = "road_segment_id"
        timestamp_col = "timestamp"

    predictions_input = df.copy()
    predictions_input[target_col] = np.nan
    if history is None:
        combined = predictions_input
        prediction_indices = combined.index
    else:
        history_rows = history.copy()
        required = {timestamp_col, road_col, target_col}
        missing = required - set(history_rows.columns)
        if missing:
            raise ValueError(f"History is missing required columns: {sorted(missing)}")
        history_rows[timestamp_col] = pd.to_datetime(history_rows[timestamp_col], errors="coerce")
        predictions_input[timestamp_col] = pd.to_datetime(predictions_input[timestamp_col], errors="coerce")
        if history_rows[timestamp_col].isna().any() or predictions_input[timestamp_col].isna().any():
            raise ValueError("History and prediction timestamps must be valid.")
        first_forecast = predictions_input.groupby(road_col)[timestamp_col].min()
        history_rows = history_rows[
            history_rows.apply(lambda row: row[timestamp_col] < first_forecast.get(row[road_col], pd.Timestamp.min), axis=1)
        ]
        combined = pd.concat([history_rows, predictions_input], ignore_index=True, sort=False)
        combined["_is_prediction"] = [False] * len(history_rows) + [True] * len(predictions_input)
        prediction_indices = combined.index[combined["_is_prediction"]]

    enriched = make_model_features(
        combined,
        target_col=target_col,
        road_col=road_col,
        timestamp_col=timestamp_col,
    )
    if history is None:
        forecast_features = enriched
    else:
        forecast_features = enriched.loc[prediction_indices]
    if feature_columns is None:
        feature_columns = [
            column for column in forecast_features.columns
            if column not in [target_col, road_col, timestamp_col]
            and pd.api.types.is_numeric_dtype(forecast_features[column])
        ]
    X = forecast_features.reindex(columns=feature_columns)
    predictions = pipeline.predict(X)
    results = forecast_features[[timestamp_col, road_col]].copy()
    results["predicted_speed"] = predictions
    results["congestion_status"] = results["predicted_speed"].apply(classify_congestion)
    return results.reset_index(drop=True)
