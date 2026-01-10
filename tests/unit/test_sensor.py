"""Unit tests for sensor entities."""

from unittest.mock import MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.owm_precipitation_forecast.const import (
    ATTR_COORDINATES,
    ATTR_FORECAST_TIME,
    ATTR_HOURLY_BREAKDOWN,
    ATTR_LAST_UPDATE,
    ATTR_LOCATION,
    ATTR_STATUS,
    ATTR_TEMPERATURE,
    DOMAIN,
    SENSOR_TYPE_DAILY_RAIN,
    SENSOR_TYPE_DAILY_SNOW,
    SENSOR_TYPE_HEALTH,
    SENSOR_TYPE_HOURLY_RAIN,
    SENSOR_TYPE_HOURLY_SNOW,
    SENSOR_TYPE_NEXT_24H_RAIN,
    SENSOR_TYPE_NEXT_24H_SNOW,
)
from custom_components.owm_precipitation_forecast.sensor import (
    OWMHealthSensor,
    OWMPrecipitationSensor,
)


@pytest.mark.unit
class TestPrecipitationSensor:
    """Test precipitation sensor."""

    def test_sensor_initialization(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test sensor initialization."""
        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        assert sensor.sensor_type == SENSOR_TYPE_HOURLY_RAIN
        assert sensor.location_name == "Test Location"
        assert sensor.unique_id == "owm_precipitation_forecast_test_location_hourly_rain"

    def test_sensor_device_info(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test sensor device info."""
        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        device_info = sensor.device_info
        assert device_info["name"] == "OWM Precipitation Test Location"
        assert device_info["manufacturer"] == "OpenWeatherMap"
        assert device_info["model"] == "One Call API 3.0"

    def test_hourly_rain_sensor_value(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test hourly rain sensor value."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        value = sensor.native_value
        assert value == 0.1  # From sample data

    def test_hourly_snow_sensor_value(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test hourly snow sensor value."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_SNOW,
        )

        value = sensor.native_value
        assert value == 1.0  # From sample data

    def test_daily_rain_sensor_value(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test daily rain sensor value."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_DAILY_RAIN,
        )

        value = sensor.native_value
        assert value == 0.5  # From sample data

    def test_daily_snow_sensor_value(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test daily snow sensor value."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_DAILY_SNOW,
        )

        value = sensor.native_value
        assert value == 5.0  # From sample data

    def test_next_24h_rain_sensor_value(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test next 24h rain sensor value."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_NEXT_24H_RAIN,
        )

        value = sensor.native_value
        assert value == 2.4  # 24 * 0.1

    def test_next_24h_snow_sensor_value(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test next 24h snow sensor value."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_NEXT_24H_SNOW,
        )

        value = sensor.native_value
        assert value == 24.0  # 24 * 1.0

    def test_sensor_value_when_no_data(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test sensor value when no data available."""
        mock_coordinator.data = None

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        value = sensor.native_value
        assert value is None


@pytest.mark.unit
class TestSensorAttributes:
    """Test sensor attributes."""

    def test_hourly_sensor_attributes(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test hourly sensor attributes."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        attributes = sensor.extra_state_attributes

        assert ATTR_LOCATION in attributes
        assert ATTR_COORDINATES in attributes
        assert ATTR_LAST_UPDATE in attributes
        assert ATTR_FORECAST_TIME in attributes
        assert ATTR_TEMPERATURE in attributes
        assert ATTR_HOURLY_BREAKDOWN in attributes
        assert "description" in attributes

        assert attributes[ATTR_LOCATION] == "Test Location"
        assert len(attributes[ATTR_HOURLY_BREAKDOWN]) == 24

    def test_daily_sensor_attributes(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test daily sensor attributes."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_DAILY_RAIN,
        )

        attributes = sensor.extra_state_attributes

        assert ATTR_LOCATION in attributes
        assert ATTR_COORDINATES in attributes
        assert ATTR_LAST_UPDATE in attributes
        assert ATTR_FORECAST_TIME in attributes
        assert ATTR_TEMPERATURE in attributes
        assert "daily_breakdown" in attributes

        temp = attributes[ATTR_TEMPERATURE]
        assert "high" in temp
        assert "low" in temp

    def test_next_24h_sensor_attributes(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test next 24h sensor attributes."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_NEXT_24H_RAIN,
        )

        attributes = sensor.extra_state_attributes

        assert ATTR_HOURLY_BREAKDOWN in attributes
        assert len(attributes[ATTR_HOURLY_BREAKDOWN]) == 24
        
        # Check breakdown structure
        breakdown = attributes[ATTR_HOURLY_BREAKDOWN]
        assert "time" in breakdown[0]
        assert "rain" in breakdown[0]
        assert "probability" in breakdown[0]
        assert "temperature" in breakdown[0]

    def test_attributes_when_no_data(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test attributes when no data available."""
        mock_coordinator.data = None

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        attributes = sensor.extra_state_attributes
        assert attributes == {}


@pytest.mark.unit
class TestHealthSensor:
    """Test health sensor."""

    def test_health_sensor_initialization(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test health sensor initialization."""
        sensor = OWMHealthSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
        )

        assert sensor.location_name == "Test Location"
        assert sensor.unique_id == "owm_precipitation_forecast_test_location_health"

    def test_health_sensor_value_ok(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test health sensor value when OK."""
        mock_coordinator.health_status.status = "ok"

        sensor = OWMHealthSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
        )

        assert sensor.native_value == "ok"

    def test_health_sensor_value_error(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test health sensor value when error."""
        mock_coordinator.health_status.status = "error"

        sensor = OWMHealthSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
        )

        assert sensor.native_value == "error"

    def test_health_sensor_attributes(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test health sensor attributes."""
        from custom_components.owm_precipitation_forecast.models import HealthStatus
        from datetime import datetime

        mock_coordinator.health_status = HealthStatus(
            status="ok",
            api_calls_today=10,
            api_calls_remaining=990,
            error_count=0,
            last_error=None,
            last_update=datetime.now(),
            next_update=None,
        )

        sensor = OWMHealthSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
        )

        attributes = sensor.extra_state_attributes

        assert ATTR_STATUS in attributes
        assert attributes[ATTR_STATUS] == "ok"
        assert attributes["api_calls_today"] == 10
        assert attributes["api_calls_remaining"] == 990
        assert attributes["error_count"] == 0
        assert ATTR_LOCATION in attributes
        assert ATTR_COORDINATES in attributes

    def test_health_sensor_icon(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test health sensor icon changes based on status."""
        sensor = OWMHealthSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
        )

        # OK status
        mock_coordinator.health_status.status = "ok"
        assert sensor.icon == "mdi:heart-pulse"

        # Warning status
        mock_coordinator.health_status.status = "warning"
        assert sensor.icon == "mdi:alert"

        # Error status
        mock_coordinator.health_status.status = "error"
        assert sensor.icon == "mdi:alert-circle"

        # Unavailable status
        mock_coordinator.health_status.status = "unavailable"
        assert sensor.icon == "mdi:help-circle"

    def test_health_sensor_always_available(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test health sensor is always available."""
        mock_coordinator.last_update_success = False

        sensor = OWMHealthSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
        )

        # Health sensor should always be available to report status
        assert sensor.available is True


@pytest.mark.unit
class TestSensorAvailability:
    """Test sensor availability."""

    def test_sensor_available_with_data(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test sensor available when data present."""
        mock_coordinator.data = sample_forecast_data
        mock_coordinator.last_update_success = True

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        assert sensor.available is True

    def test_sensor_unavailable_without_data(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test sensor unavailable when no data."""
        mock_coordinator.data = None
        mock_coordinator.last_update_success = False

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        assert sensor.available is False

    def test_sensor_unavailable_after_failed_update(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test sensor unavailable after failed update."""
        mock_coordinator.data = sample_forecast_data
        mock_coordinator.last_update_success = False

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        assert sensor.available is False


@pytest.mark.unit
class TestSensorErrorHandling:
    """Test sensor error handling."""

    def test_sensor_handles_calculation_error(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test sensor handles calculation errors gracefully."""
        # Create mock data that will cause calculation error
        mock_coordinator.data = MagicMock()
        mock_coordinator.data.hourly_forecasts = []  # Empty list

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        # Should return None instead of raising exception
        value = sensor.native_value
        assert value is None or value == 0.0

    def test_sensor_handles_attribute_error(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry, sample_forecast_data
    ):
        """Test sensor handles attribute building errors."""
        mock_coordinator.data = sample_forecast_data

        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        # Should return empty dict instead of raising
        attributes = sensor.extra_state_attributes
        assert isinstance(attributes, dict)


@pytest.mark.unit
class TestSensorEntityDescription:
    """Test sensor entity descriptions."""

    def test_sensor_has_entity_description(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test sensor has proper entity description."""
        sensor = OWMPrecipitationSensor(
            mock_coordinator,
            mock_config_entry,
            "Test Location",
            SENSOR_TYPE_HOURLY_RAIN,
        )

        assert hasattr(sensor, "entity_description")
        assert sensor.entity_description.key == SENSOR_TYPE_HOURLY_RAIN
        assert sensor.entity_description.native_unit_of_measurement == "in"

    def test_all_sensor_types_have_descriptions(
        self, hass: HomeAssistant, mock_coordinator, mock_config_entry
    ):
        """Test all sensor types have entity descriptions."""
        sensor_types = [
            SENSOR_TYPE_HOURLY_RAIN,
            SENSOR_TYPE_HOURLY_SNOW,
            SENSOR_TYPE_DAILY_RAIN,
            SENSOR_TYPE_DAILY_SNOW,
            SENSOR_TYPE_NEXT_24H_RAIN,
            SENSOR_TYPE_NEXT_24H_SNOW,
        ]

        for sensor_type in sensor_types:
            sensor = OWMPrecipitationSensor(
                mock_coordinator,
                mock_config_entry,
                "Test Location",
                sensor_type,
            )

            assert hasattr(sensor, "entity_description")
            assert sensor.entity_description.key == sensor_type
