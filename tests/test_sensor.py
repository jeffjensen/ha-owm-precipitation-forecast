"""Tests for sensor platform."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.ha_owm_precipitation_forecast.sensor import (
    async_setup_entry,
    OWMHourlyRainSensor,
    OWMNext24hSnowSensor,
    OWMHealthSensor,
)
from custom_components.ha_owm_precipitation_forecast.const import DOMAIN


@pytest.mark.asyncio
async def test_sensor_setup(hass: HomeAssistant, config_data):
    """Test sensor setup."""
    coordinator = AsyncMock()
    coordinator.latitude = config_data["latitude"]
    coordinator.longitude = config_data["longitude"]
    coordinator.data = {
        "hourly": [{"rain": 0.1, "snow": 0.05, "timestamp": 123} for _ in range(24)],
        "daily": [{"rain": 1.0, "snow": 0.5, "timestamp": 123}],
        "next24h": {"rain": 2.4, "snow": 1.2},
        "last_update": 123,
    }
    coordinator.last_error = None
    
    hass.data[DOMAIN] = {"test": coordinator}
    
    add_entities = AsyncMock()
    entry = MagicMock()
    entry.entry_id = "test"
    entry.data = config_data
    
    await async_setup_entry(hass, entry, add_entities)
    
    assert add_entities.called


def test_hourly_rain_sensor():
    """Test hourly rain sensor."""
    coordinator = AsyncMock()
    coordinator.latitude = 40.0
    coordinator.longitude = -74.0
    coordinator.last_error = None
    coordinator.data = {
        "hourly": [{"rain": 0.1, "timestamp": i} for i in range(24)],
    }
    
    sensor = OWMHourlyRainSensor(coordinator, "Test Location")
    
    assert sensor.name == "Hourly rain"
    assert sensor.native_value == 2.4
    assert sensor.native_unit_of_measurement == "in"


def test_next24h_snow_sensor():
    """Test next 24h snow sensor."""
    coordinator = AsyncMock()
    coordinator.latitude = 40.0
    coordinator.longitude = -74.0
    coordinator.last_error = None
    coordinator.data = {
        "next24h": {"rain": 1.0, "snow": 5.0},
    }
    
    sensor = OWMNext24hSnowSensor(coordinator, "Test Location")
    
    assert sensor.name == "Next 24h snow"
    assert sensor.native_value == 5.0


def test_health_sensor_ok():
    """Test health sensor in OK state."""
    coordinator = AsyncMock()
    coordinator.latitude = 40.0
    coordinator.longitude = -74.0
    coordinator.last_error = None
    coordinator.data = {}
    
    sensor = OWMHealthSensor(coordinator, "Test Location")
    
    assert sensor.native_value == "ok"


def test_health_sensor_error():
    """Test health sensor in error state."""
    coordinator = AsyncMock()
    coordinator.latitude = 40.0
    coordinator.longitude = -74.0
    coordinator.last_error = "API Error"
    coordinator.data = {}
    
    sensor = OWMHealthSensor(coordinator, "Test Location")
    
    assert sensor.native_value == "error"
