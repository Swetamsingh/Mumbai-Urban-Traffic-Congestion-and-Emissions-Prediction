from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(BaseModel):
    status: str
    model_available: bool
    dataset_available: bool


class DatasetSummary(BaseModel):
    region: str
    dataset_name: str
    data_status: str
    source: str
    geographic_coverage: str
    coverage_start: datetime
    coverage_end: datetime
    row_count: int
    segment_count: int
    mean_speed_kmh: float
    median_speed_kmh: float


class RoadSegment(BaseModel):
    road_segment_id: str
    observation_count: int
    coverage_start: datetime
    coverage_end: datetime
    mean_speed_kmh: float


class TrendPoint(BaseModel):
    label: str
    mean_speed_kmh: float
    observation_count: int


class TrendsResponse(BaseModel):
    segment_id: str | None
    hourly: list[TrendPoint]
    weekdays: list[TrendPoint]


class PredictionRequest(APIModel):
    road_segment_id: str = Field(min_length=1, max_length=100)
    forecast_timestamp: datetime
    traffic_volume: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    temperature_c: float | None = Field(default=None, ge=-80, le=70, allow_inf_nan=False)
    rainfall_mm: float | None = Field(default=None, ge=0, le=1000, allow_inf_nan=False)


class PredictionResponse(BaseModel):
    road_segment_id: str
    forecast_timestamp: datetime
    predicted_speed_kmh: float
    congestion_class: str
    forecast_horizon_hours: float
    validated_horizon_hours: float
    missing_inputs: list[str]
    data_notice: str


class EmissionsRequest(APIModel):
    vehicle_count: float = Field(ge=0, allow_inf_nan=False)
    segment_length_km: float = Field(gt=0, allow_inf_nan=False)
    emission_factor_g_per_vehicle_km: float = Field(gt=0, allow_inf_nan=False)
    observation_period: str = Field(min_length=1, max_length=100)
    emission_factor_source: str = Field(min_length=1, max_length=300)


class EmissionsResponse(BaseModel):
    co2_grams: float
    co2_kg: float
    vehicle_km: float
    vehicle_count: float
    segment_length_km: float
    emission_factor_g_per_vehicle_km: float
    observation_period: str
    emission_factor_source: str
    assumption: str
