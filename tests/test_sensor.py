"""Test sensor entities."""
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pytest_homeassistant_custom_component.common import MockConfigEntry
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.ha_owm_precipitation_forecast.const import (
    DOMAIN,
    ENTITY_PREFIX,
    UNIT_INCHES,
)
from custom_components.ha_owm_precipitation_forecast.coordinator import (
    OWMPrecipitationCoordinator,
)
from custom_components.ha_owm_precipitation_forecast.sensor import (
    OWMHealthSensor,
    OWMPrecipitationSensor,
    async_setup_entry,
)


@pytest.fixture
def mock_coordinator(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_forecast_data: dict,
) -> OWMPrecipitationCoordinator:
    """Create a mock coordinator with data."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

    # Mock the data
    coordinator.data = {
        "hourly_rain": [{"timestamp": "2021-01-01", "rain_inches": 0.197, "temperature_f": 28.0}],
        "hourly_snow": [{"timestamp": "2021-01-01", "snow_inches": 1.970, "temperature_f": 28.0}],
        "daily_rain": [{"timestamp": "2021-01-01", "rain_inches": 0.394}],
        "daily_snow": [{"timestamp": "2021-01-01", "snow_inches": 3.940}],
        "next24h_rain": 0.394,
        "next24h_snow": 3.940,
        "last_update": "2021-01-01T00:00:00",
    }

    return coordinator


def test_precipitation_sensor_initialization(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test precipitation sensor initialization."""
    sensor = OWMPrecipitationSensor(
        mock_coordinator,
        "Test Location",
        "rain_hourly",
        "Rain Hourly",
        "hourly_rain",
    )

    assert sensor._location_name == "Test Location"
    assert sensor._sensor_type == "rain_hourly"
    assert sensor._attr_unique_id == f"{ENTITY_PREFIX}_test_location_rain_hourly"


def test_precipitation_sensor_state(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test precipitation sensor state."""
    sensor = OWMPrecipitationSensor(
        mock_coordinator,
        "Test Location",
        "rain_next24h",
        "Rain Next 24h",
        "next24h_rain",
    )

    assert sensor.native_value == 0.394
    assert sensor.native_unit_of_measurement == UNIT_INCHES


def test_precipitation_sensor_attributes(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test precipitation sensor attributes."""
    sensor = OWMPrecipitationSensor(
        mock_coordinator,
        "Test Location",
        "rain_hourly",
        "Rain Hourly",
        "hourly_rain",
    )

    attrs = sensor.extra_state_attributes

    assert "forecast" in attrs
    assert "unit_of_measurement" in attrs
    assert attrs["unit_of_measurement"] == UNIT_INCHES


def test_precipitation_sensor_no_data(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test precipitation sensor with no data."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
    coordinator.data = None

    sensor = OWMPrecipitationSensor(
        coordinator,
        "Test Location",
        "rain_hourly",
        "Rain Hourly",
        "hourly_rain",
    )

    assert sensor.native_value is None


def test_health_sensor_initialization(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test health sensor initialization."""
    sensor = OWMHealthSensor(mock_coordinator, "Test Location")

    assert sensor._location_name == "Test Location"
    assert sensor._attr_unique_id == f"{ENTITY_PREFIX}_test_location_health"


def test_health_sensor_state(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test health sensor state."""
    sensor = OWMHealthSensor(mock_coordinator, "Test Location")

    assert sensor.native_value == "ok"


def test_health_sensor_attributes(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test health sensor attributes."""
    sensor = OWMHealthSensor(mock_coordinator, "Test Location")

    attrs = sensor.extra_state_attributes

    assert "message" in attrs
    assert attrs["message"] == "Operating normally"


def test_health_sensor_availability(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test health sensor is always available."""
    sensor = OWMHealthSensor(mock_coordinator, "Test Location")

    # Health sensor should always be available
    assert sensor.available is True


def test_health_sensor_icons(
    mock_coordinator: OWMPrecipitationCoordinator,
) -> None:
    """Test health sensor icon changes with status."""
    sensor = OWMHealthSensor(mock_coordinator, "Test Location")

    # OK status
    mock_coordinator._health_status = "ok"
    assert sensor.icon == "mdi:check-circle"

    # Warning status
    mock_coordinator._health_status = "warning"
    assert sensor.icon == "mdi:alert-circle"

    # Error status
    mock_coordinator._health_status = "error"
    assert sensor.icon == "mdi:alert-circle-outline"


@pytest.mark.asyncio
async def test_async_setup_entry_rain_enabled(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test sensor setup with rain enabled."""
    mock_config_entry.add_to_hass(hass)

    entities_added = []

    def mock_add_entities(entities):
        entities_added.extend(entities)

    # Mock the coordinator in hass.data
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
    hass.data[DOMAIN] = {mock_config_entry.entry_id: coordinator}

    await async_setup_entry(hass, mock_config_entry, mock_add_entities)

    # Should have rain sensors + health sensor
    assert len(entities_added) >= 4  # 3 rain + 3 snow + 1 health


@pytest.mark.asyncio
async def test_sensor_updates_with_coordinator(
    hass: HomeAssistant,
    mock_coordinator: OWMPrecipitationCoordinator,
    mock_forecast_data: dict,
) -> None:
    """Test sensor updates when coordinator refreshes."""
    sensor = OWMPrecipitationSensor(
        mock_coordinator,
        "Test",
        "rain_next24h",
        "Rain",
        "next24h_rain",
    )

    initial_value = sensor.native_value

    # Update coordinator data
    mock_coordinator.data["next24h_rain"] = 1.5

    # Sensor should reflect new value
    assert sensor.native_value == 1.5
    assert sensor.native_value != initial_value
