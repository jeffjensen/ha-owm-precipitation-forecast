"""Pytest configuration and fixtures."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component


@pytest.fixture
def hass(event_loop):
    """Fixture for Home Assistant instance."""
    hass = HomeAssistant()
    yield hass
    event_loop.run_until_complete(hass.async_block_till_done())


@pytest.fixture
def mock_owm_response() -> dict[str, Any]:
    """Mock OpenWeatherMap API response."""
    return {
        "current": {"dt": 1234567890},
        "hourly": [
            {
                "dt": 1234567890 + i * 3600,
                "temp": 15 - i * 0.5,
                "rain": {"1h": 0.5 + i * 0.1} if i % 3 == 0 else {},
                "snow": {"1h": 0.2 + i * 0.05} if i % 4 == 0 else {},
            }
            for i in range(24)
        ],
        "daily": [
            {
                "dt": 1234567890 + i * 86400,
                "temp": {"day": 20 - i},
                "rain": 2.0 + i * 0.5,
                "snow": 0.5 + i * 0.2,
            }
            for i in range(8)
        ],
    }


@pytest.fixture
def mock_weather_service(mock_owm_response):
    """Mock weather service."""
    service = AsyncMock()
    service.async_get_forecast = AsyncMock(return_value=mock_owm_response)
    return service


@pytest.fixture
def config_data() -> dict[str, Any]:
    """Configuration data for testing."""
    return {
        "api_key": "test_key_12345",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "location_name": "New York",
        "scan_interval": 60,
        "enable_rain": True,
        "enable_snow": True,
        "snow_ratio": 10.0,
        "temperature_adjusted_ratio": True,
    }
