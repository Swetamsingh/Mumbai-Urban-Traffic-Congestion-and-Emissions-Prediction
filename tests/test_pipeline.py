import numpy as np
import pandas as pd
import yaml

from traffic_ml.data import generate_sample_data
from traffic_ml.evaluate import evaluate_model
from traffic_ml.predict import predict_traffic
from traffic_ml.train import chronological_split, train_model


def test_chronological_split_keeps_same_timestamp_in_one_partition():
    rows = [
        {"timestamp": timestamp, "road_segment_id": road, "traffic_speed_kmh": 40.0}
        for timestamp in pd.date_range("2025-01-01", periods=10, freq="h")
        for road in ["A", "B"]
    ]
    train, validation, test = chronological_split(
        pd.DataFrame(rows), test_fraction=0.2, validation_fraction=0.2
    )

    assert train["timestamp"].max() < validation["timestamp"].min()
    assert validation["timestamp"].max() < test["timestamp"].min()
    assert set(train["road_segment_id"]) == {"A", "B"}
    assert set(validation["road_segment_id"]) == {"A", "B"}
    assert set(test["road_segment_id"]) == {"A", "B"}


def test_train_evaluate_predict_share_saved_feature_schema(tmp_path):
    data_path = tmp_path / "traffic.csv"
    model_path = tmp_path / "traffic.joblib"
    metrics_path = tmp_path / "metrics.json"
    config_path = tmp_path / "config.yaml"
    sample = generate_sample_data(data_path)
    config_path.write_text(
        yaml.safe_dump(
            {
                "data": {
                    "input_path": str(data_path),
                    "processed_path": str(tmp_path / "processed.csv"),
                    "timestamp_column": "timestamp",
                    "road_id_column": "road_segment_id",
                    "target_column": "traffic_speed_kmh",
                    "model_path": str(model_path),
                    "metrics_path": str(metrics_path),
                },
                "training": {
                    "test_fraction": 0.2,
                    "validation_fraction": 0.15,
                    "random_state": 42,
                },
            }
        ),
        encoding="utf-8",
    )

    trained_metrics = train_model(config_path)
    evaluated_metrics = evaluate_model(model_path, data_path, config_path)
    history = sample[sample["road_segment_id"] == "ROAD_01"].iloc[:24]
    forecast = pd.DataFrame(
        [{
            "timestamp": history["timestamp"].max() + pd.Timedelta(hours=1),
            "road_segment_id": "ROAD_01",
            "traffic_volume": 500,
            "temperature_c": 20,
            "rainfall_mm": 0,
        }]
    )
    predictions = predict_traffic(model_path, forecast, history=history)

    assert trained_metrics["baseline"]["mae"] > trained_metrics["mae"]
    assert evaluated_metrics["test_rows"] == trained_metrics["test_rows"]
    assert np.isfinite(predictions["predicted_speed"]).all()
    assert predictions.iloc[0]["road_segment_id"] == "ROAD_01"
