from __future__ import annotations

from ..schemas import EmissionsRequest, EmissionsResponse
from traffic_ml.emissions import estimate_emissions


DEFAULT_FACTOR_SOURCE = "Illustrative prototype input; replace with a cited local source"


def create_emissions_estimate(request: EmissionsRequest) -> EmissionsResponse:
    estimate = estimate_emissions(
        request.vehicle_count,
        request.segment_length_km,
        request.emission_factor_g_per_vehicle_km,
    )
    vehicle_km = request.vehicle_count * request.segment_length_km
    return EmissionsResponse(
        **estimate,
        vehicle_km=vehicle_km,
        observation_period=request.observation_period,
        emission_factor_source=request.emission_factor_source,
        assumption=(
            "Estimated from vehicle-kilometres and a constant average factor. "
            "This is not a measured emission value; vehicle mix and local conditions are not modeled."
        ),
    )
