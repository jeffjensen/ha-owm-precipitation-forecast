"""Pytest configuration for OWM Precipitation Forecast tests."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.owm_precipitation_forecast.const import DOMAIN
from custom_components.owm_precipitation_forecast.client import OWMCoordinates


@pytest.fixture
def mock_owm_response():
    """Fixture for mock OWM API response."""
    return {
        "hourly": [
            {
                "dt": 1735699200,  # 2025-01-01 00:00 UTC
                "temp": 0.0,  # 32°F
                "rain": {"1h": 2.54},  # 0.1 inches
                "snow": {"1h": 0.0},
            },
            {
                "dt": 1735702800,  # Next hour
                "temp": -1.11,  # 30°F
                "rain": {"1h": 0.0},
                "snow": {"1h": 5.08},  # 0.2 inches liquid
            },
        ],
        "daily": [
            {
                "dt": 1735699200,
                "temp": {"day": 1.11, "min": -1.11, "max": 4.44},  # 34°F avg
                "rain": 5.08,  # 0.2 inches
                "snow": 0.0,
            }
        ],
    }


@pytest.fixture
def hass(mock_owm_response):
    """Fixture for mocked Home Assistant."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    return hass


@pytest.fixture
def mock_coords():
    """Mock coordinates."""
    return OWMCoordinates(latitude=40.7128, longitude=-74.0060)


@pytest.fixture
def mock_config_entry(hass, mock_coords):
    """Mock config entry."""
    entry = MagicMock()
    entry.data = {
        "api_key": "test_key",
        "location_name": "Test Home",
        "location_slug": "test_home",
        "latitude": 40.7128,
        "longitude": -74.0060,
    }
    entry.entry_id = "test_entry_id"
    entry.options = {"polling_interval": 60, "snow_ratio_mode": "preset"}
    return entry
