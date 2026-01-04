"""Test fixtures and configuration."""
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_owm_precipitation_forecast.const import (
    CONF_API_KEY,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    DOMAIN,
)


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test Location",
        data={
            CONF_API_KEY: "test_api_key_12345",
            CONF_LATITUDE: 40.7128,
            CONF_LONGITUDE: -74.0060,
            CONF_LOCATION_NAME: "Test Location",
            CONF_ENABLE_RAIN: True,
            CONF_ENABLE_SNOW: True,
        },
        entry_id="test_entry_id_123",
    )


@pytest.fixture
def mock_forecast_data() -> dict:
    """Return mock OpenWeatherMap forecast data."""
    return {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "hourly": [
            {
                "dt": 1609459200,  # 2021-01-01 00:00:00
                "temp": 28.0,
                "rain": {"1h": 5.0},  # 5mm rain
            },
            {
                "dt": 1609462800,  # 2021-01-01 01:00:00
                "temp": 25.0,
                "rain": {"1h": 3.0},  # 3mm rain
            },
            {
                "dt": 1609466400,  # 2021-01-01 02:00:00
                "temp": 22.0,
                "rain": {"1h": 2.5},  # 2.5mm rain
            },
        ],
        "daily": [
            {
                "dt": 1609459200,
                "temp": {"day": 30.0, "min": 25.0, "max": 35.0},
                "rain": 10.0,  # 10mm rain for the day
            },
            {
                "dt": 1609545600,
                "temp": {"day": 28.0, "min": 20.0, "max": 32.0},
                "rain": 15.0,
            },
        ],
    }


@pytest.fixture
def mock_empty_forecast_data() -> dict:
    """Return mock forecast data with no precipitation."""
    return {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "hourly": [
            {
                "dt": 1609459200,
                "temp": 35.0,
                "rain": {"1h": 0.0},
            },
        ],
        "daily": [
            {
                "dt": 1609459200,
                "temp": {"day": 35.0},
                "rain": 0.0,
            },
        ],
    }
