import pytest

from traffic_ml.emissions import estimate_co2, estimate_emissions


def test_emissions_calculation():
    result = estimate_emissions(100, 2.5, 180)
    assert result["co2_grams"] == pytest.approx(45000.0)
    assert result["co2_kg"] == pytest.approx(45.0)


def test_negative_volume_rejected():
    with pytest.raises(ValueError):
        estimate_co2(-1, 2.0, 180.0)


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_non_finite_inputs_rejected(value):
    with pytest.raises(ValueError, match="finite non-negative"):
        estimate_co2(value, 2.0, 180.0)
