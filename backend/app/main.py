from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAFFIC_SRC = PROJECT_ROOT / "src"
if str(TRAFFIC_SRC) not in sys.path:
    sys.path.insert(0, str(TRAFFIC_SRC))

from .schemas import (
    DatasetSummary,
    EmissionsRequest,
    EmissionsResponse,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    RoadSegment,
    TrendsResponse,
)
from .services.emissions import create_emissions_estimate
from .services.prediction import (
    get_model_metrics,
    get_segments,
    get_summary,
    get_trends,
    load_config,
    predict,
    resolve_project_path,
)

app = FastAPI(
    title="Mumbai Urban Traffic Prediction API",
    description=(
        "Decision-support API for traffic speed and emissions estimates. "
        "Current traffic inputs are synthetic demonstration data, not measured Mumbai data."
    ),
    version="1.0.0",
)

origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    config = load_config()["data"]
    dataset_available = resolve_project_path(config["input_path"]).exists()
    model_available = resolve_project_path(config["model_path"]).exists()
    return HealthResponse(
        status="ok",
        model_available=model_available,
        dataset_available=dataset_available,
    )


@app.get("/api/summary", response_model=DatasetSummary)
def summary() -> DatasetSummary:
    return DatasetSummary(**get_summary())


@app.get("/api/segments", response_model=list[RoadSegment])
def segments() -> list[RoadSegment]:
    return [RoadSegment(**row) for row in get_segments()]


@app.get("/api/trends", response_model=TrendsResponse)
def trends(segment_id: str | None = Query(default=None, min_length=1, max_length=100)) -> TrendsResponse:
    return TrendsResponse(**get_trends(segment_id))


@app.post("/api/predict", response_model=PredictionResponse)
def predict_traffic(request: PredictionRequest) -> PredictionResponse:
    return PredictionResponse(**predict(request))


@app.post("/api/emissions/estimate", response_model=EmissionsResponse)
def estimate_emissions(request: EmissionsRequest) -> EmissionsResponse:
    return create_emissions_estimate(request)


@app.get("/api/model-metrics")
def model_metrics() -> dict:
    return get_model_metrics()
