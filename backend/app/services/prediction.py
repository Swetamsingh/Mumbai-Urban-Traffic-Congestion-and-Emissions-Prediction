from __future__ import annotations

import json
import sys
from datetime import timezone
from pathlib import Path

import pandas as pd
import yaml
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRAFFIC_SRC = PROJECT_ROOT / "src"
if str(TRAFFIC_SRC) not in sys.path:
    sys.path.insert(0, str(TRAFFIC_SRC))

from traffic_ml.data import load_or_generate_sample_data, validate_and_clean
from traffic_ml.features import classify_congestion, make_model_features
from traffic_ml.predict import predict_traffic

REGION = "Mumbai urban region, Maharashtra, India"
DATASET_NAME = "Synthetic urban traffic sample"
DATA_STATUS = "Synthetic demonstration data; not Mumbai observations"
DATA_SOURCE = "Generated locally for software demonstration"
GEOGRAPHIC_COVERAGE = "No verified geographic coverage; road IDs are illustrative"
VALIDATED_HORIZON_HOURS = 1.0


def load_config() -> dict:
    config_path = PROJECT_ROOT / "configs" / "config.yaml"
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def resolve_project_path(path: str | Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else PROJECT_ROOT / value


def load_dataset() -> pd.DataFrame:
    data_config = load_config()["data"]
    raw = load_or_generate_sample_data(resolve_project_path(data_config["input_path"]))
    return validate_and_clean(
        raw,
        data_config["timestamp_column"],
        data_config["road_id_column"],
        data_config["target_column"],
    )


def get_summary() -> dict:
    config = load_config()["data"]
    frame = load_dataset()
    timestamp_column = config["timestamp_column"]
    target_column = config["target_column"]
    road_column = config["road_id_column"]
    return {
        "region": REGION,
        "dataset_name": DATASET_NAME,
        "data_status": DATA_STATUS,
        "source": DATA_SOURCE,
        "geographic_coverage": GEOGRAPHIC_COVERAGE,
        "coverage_start": frame[timestamp_column].min().to_pydatetime(),
        "coverage_end": frame[timestamp_column].max().to_pydatetime(),
        "row_count": int(len(frame)),
        "segment_count": int(frame[road_column].nunique()),
        "mean_speed_kmh": float(frame[target_column].mean()),
        "median_speed_kmh": float(frame[target_column].median()),
    }


def get_segments() -> list[dict]:
    config = load_config()["data"]
    frame = load_dataset()
    timestamp_column = config["timestamp_column"]
    target_column = config["target_column"]
    road_column = config["road_id_column"]
    grouped = frame.groupby(road_column).agg(
        observation_count=(target_column, "count"),
        coverage_start=(timestamp_column, "min"),
        coverage_end=(timestamp_column, "max"),
        mean_speed_kmh=(target_column, "mean"),
    )
    grouped.index.name = "road_segment_id"
    return grouped.reset_index().to_dict(orient="records")


def get_trends(segment_id: str | None = None) -> dict:
    config = load_config()["data"]
    frame = load_dataset()
    road_column = config["road_id_column"]
    target_column = config["target_column"]
    timestamp_column = config["timestamp_column"]
    if segment_id is not None:
        frame = frame[frame[road_column] == segment_id]
        if frame.empty:
            raise HTTPException(status_code=404, detail=f"Unknown road segment: {segment_id}")

    features = make_model_features(
        frame,
        target_col=target_column,
        road_col=road_column,
        timestamp_col=timestamp_column,
    )
    features["weekday"] = pd.to_datetime(features[timestamp_column]).dt.dayofweek
    hourly = (
        features.groupby("hour")[target_column]
        .agg(mean_speed_kmh="mean", observation_count="count")
        .reindex(range(24))
    )
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekdays = (
        features.groupby("weekday")[target_column]
        .agg(mean_speed_kmh="mean", observation_count="count")
        .reindex(range(7))
    )
    return {
        "segment_id": segment_id,
        "hourly": [
            {
                "label": f"{hour:02d}:00",
                "mean_speed_kmh": float(row["mean_speed_kmh"]),
                "observation_count": int(row["observation_count"]),
            }
            for hour, row in hourly.dropna().iterrows()
        ],
        "weekdays": [
            {
                "label": weekday_names[day],
                "mean_speed_kmh": float(row["mean_speed_kmh"]),
                "observation_count": int(row["observation_count"]),
            }
            for day, row in weekdays.dropna().iterrows()
        ],
    }


def predict(request) -> dict:
    config = load_config()
    data_config = config["data"]
    model_path = resolve_project_path(data_config["model_path"])
    if not model_path.exists():
        raise HTTPException(
            status_code=503,
            detail="No trained model is available. Train it with python -m traffic_ml.train first.",
        )

    frame = load_dataset()
    road_column = data_config["road_id_column"]
    timestamp_column = data_config["timestamp_column"]
    target_column = data_config["target_column"]
    segment_rows = frame[frame[road_column] == request.road_segment_id]
    if segment_rows.empty:
        raise HTTPException(status_code=404, detail=f"Unknown road segment: {request.road_segment_id}")

    forecast_time = request.forecast_timestamp
    if forecast_time.tzinfo is not None:
        forecast_time = forecast_time.astimezone(timezone.utc).replace(tzinfo=None)
    forecast_time = pd.Timestamp(forecast_time)
    history = segment_rows[segment_rows[timestamp_column] < forecast_time]
    if history.empty:
        raise HTTPException(
            status_code=422,
            detail="Prediction time must be later than at least one observed reading for this segment.",
        )
    latest_observation = pd.Timestamp(history[timestamp_column].max())
    horizon_hours = (forecast_time - latest_observation).total_seconds() / 3600

    prediction_row = {
        timestamp_column: forecast_time,
        road_column: request.road_segment_id,
        target_column: None,
        "traffic_volume": request.traffic_volume,
        "temperature_c": request.temperature_c,
        "rainfall_mm": request.rainfall_mm,
    }
    predictions = predict_traffic(
        model_path,
        pd.DataFrame([prediction_row]),
        target_col=target_column,
        history=history,
    )
    predicted_speed = float(predictions.iloc[0]["predicted_speed"])
    if not pd.notna(predicted_speed):
        raise HTTPException(status_code=500, detail="The model returned a non-finite prediction.")

    omitted_inputs = [
        name
        for name, value in [
            ("traffic_volume", request.traffic_volume),
            ("temperature_c", request.temperature_c),
            ("rainfall_mm", request.rainfall_mm),
        ]
        if value is None
    ]
    return {
        "road_segment_id": request.road_segment_id,
        "forecast_timestamp": forecast_time.to_pydatetime(),
        "predicted_speed_kmh": predicted_speed,
        "congestion_class": classify_congestion(
            predicted_speed,
            config["congestion"]["low_speed_max_kmh"],
            config["congestion"]["moderate_speed_min_kmh"],
        ),
        "forecast_horizon_hours": round(horizon_hours, 2),
        "validated_horizon_hours": VALIDATED_HORIZON_HOURS,
        "missing_inputs": omitted_inputs,
        "data_notice": (
            "Prediction is generated from synthetic demo traffic data, not verified Mumbai observations. "
            "Forecasts beyond one hour have not been validated."
        ),
    }


def get_model_metrics() -> dict:
    metrics_path = resolve_project_path(load_config()["data"]["metrics_path"])
    if not metrics_path.exists():
        return {"available": False, "message": "No saved metrics. Train and evaluate the model first."}
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["available"] = True
    metrics["data_notice"] = DATA_STATUS
    return metrics
