"""Test sensor entities."""
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import STATE_UNAVAILABLE

from custom_components.owm_precipitation_forecast.sensor import (
    DailyCombinedPrecipitationSensor,
    HourlyCombinedPrecipitationSensor,
    Next24hCombinedPrecipitationSensor,
)


async def test_hourly_sensor_state(hass, mock_config_entry, mock_owm_response):
    """Test hourly sensor state and attributes."""
    # Mock coordinator data
    coordinator = MagicMock()
    coordinator.data = mock_owm_response
    coordinator.last_update_success = True

    sensor = HourlyCombinedPrecipitationSensor(
        coordinator, MagicMock(), "test_home", "Test Home", "test_entry"
    )

    assert sensor.native_value == pytest.approx(0.1)  # rain only for first hour
    attrs = sensor.extra_state_attributes
    assert attrs["rain_inches"] == pytest.approx(0.1)
    assert "snow_inches" in attrs


async def test_sensor_unavailable_when_coordinator_fails(hass, mock_config_entry):
    """Sensor shows unavailable when coordinator fails."""
    coordinator = MagicMock()
    coordinator.last_update_success = False

    sensor = Next24hCombinedPrecipitationSensor(
        coordinator, MagicMock(), "test_home", "Test Home", "test_entry"
    )

    assert sensor.available is False
