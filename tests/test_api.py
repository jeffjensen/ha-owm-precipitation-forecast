"""Test OWM data transformation."""
import pytest
from datetime import datetime, timezone

from custom_components.owm_precipitation_forecast.api import (
    HourlyPoint,
    OWMPrecipitationTransformer,
)
from custom_components.owm_precipitation_forecast.snow_ratio import SnowRatioCalculator


@pytest.fixture
def transformer():
    """Transformer with default snow ratios."""
    snow_ratio = SnowRatioCalculator({"below_0f": 10, "0_to_15f": 10, "15_to_32f": 10, "above_32f": 0})
    return OWMPrecipitationTransformer(snow_ratio)


def test_build_hourly_points(transformer, mock_owm_response):
    """Test hourly point transformation."""
    hourly = mock_owm_response["hourly"]
    points = transformer.build_hourly_points(hourly)

    assert len(points) == 2
    assert isinstance(points[0], HourlyPoint)
    assert points[0].rain_inches == pytest.approx(0.1)
    assert points[0].timestamp == datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)


def test_summarize_next24h(transformer, mock_owm_response):
    """Test 24h summary."""
    hourly = mock_owm_response["hourly"]
    points = transformer.build_hourly_points(hourly)
    summary = transformer.summarize_next24h(points)

    assert "rain_inches" in summary
    assert "snow_inches" in summary
    assert summary["rain_inches"] == pytest.approx(0.1)
