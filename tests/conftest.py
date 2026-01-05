"""Fixtures for testing."""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_owm_precipitation_forecast.const import DOMAIN


@pytest.fixture
def mock_owm_client():
    """Mock OWM client."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.owm_client.OpenWeatherMapClient"
    ) as mock_client:
        client = mock_client.return_value
        client.get_forecast_data = AsyncMock(return_value=get_mock_forecast_data())
        client.validate_credentials = AsyncMock()
        client.close = AsyncMock()
        yield client


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "location_name": "Test Location",
            "latitude": 44.9778,
            "longitude": -93.2650,
            "api_key": "test_api_key_12345",
            "enable_rain": True,
            "enable_snow": True,
            "update_interval": "60",
        },
        entry_id="test_entry_id",
        unique_id="44.9778_-93.2650_Test Location",
    )


def get_mock_forecast_data():
    """Return mock forecast data."""
    return {
        "hourly": [
            {
                "timestamp": "2026-01-03T12:00:00+00:00",
                "temperature": 28.5,
                "rain": 0.0,
                "snow": 2.5,
            },
            {
                "timestamp": "2026-01-03T13:00:00+00:00",
                "temperature": 27.8,
                "rain": 0.0,
                "snow": 3.2,
            },
            {
                "timestamp": "2026-01-03T14:00:00+00:00",
                "temperature": 30.1,
                "rain": 1.5,
                "snow": 0.0,
            },
        ] * 16,  # 48 hours
        "daily": [
            {
                "timestamp": "2026-01-03T00:00:00+00:00",
                "temperature": 28.0,
                "rain": 5.0,
                "snow": 10.0,
            },
            {
                "timestamp": "2026-01-04T00:00:00+00:00",
                "temperature": 32.5,
                "rain": 8.0,
                "snow": 0.0,
            },
        ] * 4,  # 7 days
        "location": {
            "latitude": 44.9778,
            "longitude": -93.2650,
            "timezone": "America/Chicago",
        },
    }
