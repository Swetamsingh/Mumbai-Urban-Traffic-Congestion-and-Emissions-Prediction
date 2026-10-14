from __future__ import annotations

import math


def _validate_non_negative_finite(name: str, value: float) -> float:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite non-negative number.") from exc
    if not math.isfinite(numeric_value) or numeric_value < 0:
        raise ValueError(f"{name} must be a finite non-negative number.")
    return numeric_value


def estimate_co2(vehicle_count: float, segment_length_km: float, emission_factor_g_per_vehicle_km: float) -> float:
    """Estimate CO2 emissions in grams for a segment in a time period."""
    count = _validate_non_negative_finite("Vehicle count", vehicle_count)
    length = _validate_non_negative_finite("Segment length", segment_length_km)
    factor = _validate_non_negative_finite("Emission factor", emission_factor_g_per_vehicle_km)
    return count * length * factor


def estimate_emissions(vehicle_count: float, segment_length_km: float, emission_factor_g_per_vehicle_km: float) -> dict:
    count = _validate_non_negative_finite("Vehicle count", vehicle_count)
    length = _validate_non_negative_finite("Segment length", segment_length_km)
    factor = _validate_non_negative_finite("Emission factor", emission_factor_g_per_vehicle_km)
    grams = estimate_co2(count, length, factor)
    return {
        "co2_grams": grams,
        "co2_kg": grams / 1000.0,
        "vehicle_count": count,
        "segment_length_km": length,
        "emission_factor_g_per_vehicle_km": factor,
    }
