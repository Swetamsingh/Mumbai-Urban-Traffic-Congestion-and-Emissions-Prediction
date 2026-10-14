import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.main import app
from backend.app.schemas import PredictionRequest
from src.traffic_ml.train import train_model


@pytest.fixture(scope="module", autouse=True)
def trained_model():
    train_model()


@pytest.fixture
def client():
    return TestClient(app)


def test_health_and_dataset_summary(client):
    health = client.get("/health")
    summary = client.get("/api/summary")

    assert health.status_code == 200
    assert health.json()["model_available"] is True
    assert summary.status_code == 200
    assert summary.json()["region"] == "Mumbai urban region, Maharashtra, India"
    assert "not Mumbai observations" in summary.json()["data_status"]
    assert summary.json()["row_count"] == 144


def test_segments_and_historical_trends(client):
    segments = client.get("/api/segments")
    trends = client.get("/api/trends", params={"segment_id": "ROAD_01"})

    assert segments.status_code == 200
    assert {row["road_segment_id"] for row in segments.json()} == {"ROAD_01", "ROAD_02", "ROAD_03"}
    assert trends.status_code == 200
    assert len(trends.json()["hourly"]) == 24
    assert {row["label"] for row in trends.json()["weekdays"]} == {"Monday", "Tuesday"}


def test_prediction_uses_segment_history_and_validates_segment(client):
    response = client.post(
        "/api/predict",
        json={
            "road_segment_id": "ROAD_01",
            "forecast_timestamp": "2024-01-03T00:00:00",
            "traffic_volume": 500,
            "temperature_c": 20,
            "rainfall_mm": 0,
        },
    )

    assert response.status_code == 200
    assert response.json()["predicted_speed_kmh"] > 0
    assert response.json()["forecast_horizon_hours"] == 1
    assert response.json()["congestion_class"] in {"Low", "Moderate", "High", "Severe"}

    unknown = client.post(
        "/api/predict",
        json={"road_segment_id": "UNKNOWN", "forecast_timestamp": "2024-01-03T00:00:00"},
    )
    assert unknown.status_code == 404


def test_prediction_rejects_negative_and_non_finite_inputs(client):
    response = client.post(
        "/api/predict",
        json={
            "road_segment_id": "ROAD_01",
            "forecast_timestamp": "2024-01-03T00:00:00",
            "traffic_volume": -1,
        },
    )
    assert response.status_code == 422

    with pytest.raises(ValidationError):
        PredictionRequest.model_validate(
            {
                "road_segment_id": "ROAD_01",
                "forecast_timestamp": "2024-01-03T00:00:00",
                "traffic_volume": float("nan"),
            }
        )


def test_emissions_validation_and_metrics(client):
    estimate = client.post(
        "/api/emissions/estimate",
        json={
            "vehicle_count": 100,
            "segment_length_km": 2.5,
            "emission_factor_g_per_vehicle_km": 180,
            "observation_period": "one hour",
            "emission_factor_source": "Illustrative test factor",
        },
    )
    invalid = client.post(
        "/api/emissions/estimate",
        json={
            "vehicle_count": -1,
            "segment_length_km": 2.5,
            "emission_factor_g_per_vehicle_km": 180,
            "observation_period": "one hour",
            "emission_factor_source": "test",
        },
    )
    metrics = client.get("/api/model-metrics")

    assert estimate.status_code == 200
    assert estimate.json()["co2_grams"] == pytest.approx(45000)
    assert estimate.json()["vehicle_km"] == pytest.approx(250)
    assert invalid.status_code == 422
    assert metrics.status_code == 200
    assert metrics.json()["available"] is True
