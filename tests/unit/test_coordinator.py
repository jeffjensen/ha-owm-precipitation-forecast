"""Unit tests for coordinator."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.owm_precipitation_forecast.const import (
    CONF_POLLING_INTERVAL,
    CONF_SNOW_RATIOS,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_SNOW_RATIOS,
    HEALTH_STATUS_ERROR,
    HEALTH_STATUS_OK,
    HEALTH_STATUS_WARNING,
    OWM_RATE_LIMIT_CALLS,
)
from custom_components.owm_precipitation_forecast.coordinator import (
    OWMPrecipitationCoordinator,
)
from custom_components.owm_precipitation_forecast.exceptions import (
    OWMApiConnectionError,
    OWMApiKeyError,
    OWMApiRateLimitError,
)


@pytest.mark.unit
class TestCoordinatorInitialization:
    """Test coordinator initialization."""

    def test_coordinator_init(self, hass: HomeAssistant, mock_config_entry):
        """Test coordinator initialization."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        assert coordinator.location_name == "Test Location"
        assert coordinator.latitude == 45.0
        assert coordinator.longitude == -93.0
        assert coordinator.snow_ratios == DEFAULT_SNOW_RATIOS
        assert coordinator.api_client is not None
        assert coordinator.api_stats is not None

    def test_coordinator_with_custom_options(self, hass: HomeAssistant, mock_config_entry):
        """Test coordinator with custom options."""
        custom_ratios = {"32": 15.0, "28": 18.0}
        mock_config_entry.options[CONF_SNOW_RATIOS] = custom_ratios
        mock_config_entry.options[CONF_POLLING_INTERVAL] = 7200  # 2 hours

        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        assert coordinator.snow_ratios == custom_ratios
        assert coordinator.update_interval.total_seconds() == 7200


@pytest.mark.unit
class TestCoordinatorDataUpdate:
    """Test coordinator data update."""

    @pytest.mark.asyncio
    async def test_successful_update(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test successful data update."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            data = await coordinator._async_update_data()

            assert data is not None
            assert data.location_name == "Test Location"
            assert data.latitude == 45.0
            assert data.longitude == -93.0
            assert len(data.hourly_forecasts) > 0
            assert len(data.daily_forecasts) > 0

    @pytest.mark.asyncio
    async def test_update_increments_api_stats(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test update increments API statistics."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        initial_count = coordinator.api_stats.total_calls_today

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            await coordinator._async_update_data()

            assert coordinator.api_stats.total_calls_today == initial_count + 1
            assert coordinator.api_stats.last_call_time is not None

    @pytest.mark.asyncio
    async def test_update_with_api_key_error(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test update with API key error."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            side_effect=OWMApiKeyError("Invalid API key"),
        ):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

            assert coordinator.health_status.status == HEALTH_STATUS_ERROR
            assert coordinator.api_stats.error_count > 0

    @pytest.mark.asyncio
    async def test_update_with_rate_limit_error(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test update with rate limit error."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            side_effect=OWMApiRateLimitError("Rate limit exceeded"),
        ):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

            assert coordinator.health_status.status == HEALTH_STATUS_ERROR
            assert "rate limit" in coordinator.health_status.last_error.lower()

    @pytest.mark.asyncio
    async def test_update_with_connection_error(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test update with connection error."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            side_effect=OWMApiConnectionError("Connection failed"),
        ):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

            assert coordinator.health_status.status == HEALTH_STATUS_ERROR
            assert coordinator.api_stats.error_count > 0


@pytest.mark.unit
class TestCoordinatorRateLimiting:
    """Test coordinator rate limiting."""

    def test_should_throttle_below_threshold(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test throttle check below threshold."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        coordinator.api_stats.total_calls_today = 500

        assert not coordinator._should_throttle()

    def test_should_throttle_at_threshold(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test throttle check at 80% threshold."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        coordinator.api_stats.total_calls_today = int(OWM_RATE_LIMIT_CALLS * 0.8)

        assert coordinator._should_throttle()

    def test_should_throttle_above_threshold(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test throttle check above threshold."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        coordinator.api_stats.total_calls_today = 900

        assert coordinator._should_throttle()

    @pytest.mark.asyncio
    async def test_throttle_prevents_update(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test throttling prevents update."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        coordinator.api_stats.total_calls_today = OWM_RATE_LIMIT_CALLS

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        assert coordinator.health_status.status == HEALTH_STATUS_WARNING

    def test_daily_counter_reset(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test daily counter reset."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        
        coordinator.api_stats.total_calls_today = 500
        coordinator.api_stats.last_call_time = datetime.now() - timedelta(days=2)

        coordinator._update_api_calls_tracking()

        # Counter should be reset after 1+ day
        assert coordinator.api_stats.total_calls_today == 0


@pytest.mark.unit
class TestCoordinatorHealthStatus:
    """Test coordinator health status."""

    def test_initial_health_status(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test initial health status."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        assert coordinator.health_status.status == HEALTH_STATUS_OK
        assert coordinator.health_status.error_count == 0
        assert coordinator.health_status.api_calls_today == 0

    def test_health_status_after_error(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test health status after error."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        coordinator.api_stats.increment_errors("Test error")
        coordinator._update_health_status(HEALTH_STATUS_ERROR, "Test error")

        assert coordinator.health_status.status == HEALTH_STATUS_ERROR
        assert coordinator.health_status.error_count == 1
        assert coordinator.health_status.last_error == "Test error"

    def test_health_status_recovery(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test health status recovery."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        # Set error state
        coordinator.api_stats.increment_errors("Error")
        coordinator._update_health_status(HEALTH_STATUS_ERROR, "Error")

        # Recover
        coordinator._update_health_status(HEALTH_STATUS_OK)

        assert coordinator.health_status.status == HEALTH_STATUS_OK
        assert coordinator.health_status.last_update is not None

    def test_clear_errors(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test clearing errors."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        coordinator.api_stats.increment_errors("Error 1")
        coordinator.api_stats.increment_errors("Error 2")
        coordinator._update_health_status(HEALTH_STATUS_ERROR, "Error")

        coordinator.clear_errors()

        assert coordinator.api_stats.error_count == 0
        assert coordinator.api_stats.last_error is None
        assert coordinator.health_status.status == HEALTH_STATUS_OK


@pytest.mark.unit
class TestCoordinatorDataProcessing:
    """Test coordinator data processing."""

    @pytest.mark.asyncio
    async def test_process_hourly_forecasts(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test processing hourly forecasts."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            data = await coordinator._async_update_data()

            assert len(data.hourly_forecasts) == 48
            for forecast in data.hourly_forecasts:
                assert forecast.timestamp is not None
                assert forecast.temperature_f is not None
                assert forecast.rain_inches >= 0
                assert forecast.snow_inches >= 0

    @pytest.mark.asyncio
    async def test_process_daily_forecasts(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test processing daily forecasts."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            data = await coordinator._async_update_data()

            assert len(data.daily_forecasts) == 8
            for forecast in data.daily_forecasts:
                assert forecast.date is not None
                assert forecast.temperature_high_f is not None
                assert forecast.temperature_low_f is not None
                assert forecast.rain_inches >= 0
                assert forecast.snow_inches >= 0

    @pytest.mark.asyncio
    async def test_handle_partial_data(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test handling partial OWM response."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        partial_response = {
            "lat": 45.0,
            "lon": -93.0,
            "timezone": "UTC",
            "hourly": [
                {
                    "dt": int(datetime.now().timestamp()),
                    "temp": 10,
                    "rain": {},
                    "pop": 0,
                }
            ],
            # No daily data
        }

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=partial_response,
        ):
            data = await coordinator._async_update_data()

            assert data is not None
            assert len(data.hourly_forecasts) > 0
            assert len(data.daily_forecasts) == 0  # Gracefully handle missing data

    @pytest.mark.asyncio
    async def test_handle_malformed_forecast_entry(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test handling malformed forecast entries."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        response_with_bad_entry = {
            "lat": 45.0,
            "lon": -93.0,
            "timezone": "UTC",
            "hourly": [
                {"dt": int(datetime.now().timestamp()), "temp": 10, "rain": {}, "pop": 0},
                {"dt": "invalid"},  # Malformed entry
                {"dt": int(datetime.now().timestamp()), "temp": 15, "rain": {}, "pop": 0},
            ],
            "daily": [],
        }

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=response_with_bad_entry,
        ):
            data = await coordinator._async_update_data()

            # Should skip malformed entry and process valid ones
            assert data is not None
            assert len(data.hourly_forecasts) == 2  # Only valid entries


@pytest.mark.unit
class TestCoordinatorOptionsUpdate:
    """Test coordinator options update."""

    @pytest.mark.asyncio
    async def test_update_snow_ratios(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test updating snow ratios."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        new_ratios = {"32": 12.0, "28": 15.0}
        mock_config_entry.options[CONF_SNOW_RATIOS] = new_ratios

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            await coordinator.async_update_options()

            assert coordinator.snow_ratios == new_ratios

    @pytest.mark.asyncio
    async def test_update_polling_interval(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test updating polling interval."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        initial_interval = coordinator.update_interval

        mock_config_entry.options[CONF_POLLING_INTERVAL] = 7200  # 2 hours

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            await coordinator.async_update_options()

            assert coordinator.update_interval != initial_interval
            assert coordinator.update_interval.total_seconds() == 7200


@pytest.mark.unit
class TestCoordinatorEventFiring:
    """Test coordinator event firing."""

    @pytest.mark.asyncio
    async def test_fire_update_event(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test firing update event."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        events = []

        def capture_event(event):
            events.append(event)

        hass.bus.async_listen("owm_precipitation_forecast_forecast_updated", capture_event)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            await coordinator._async_update_data()

        # Event should be fired
        assert len(events) > 0
        assert events[0].data["location"] == "Test Location"

    @pytest.mark.asyncio
    async def test_fire_error_event(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test firing error event."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        events = []

        def capture_event(event):
            events.append(event)

        hass.bus.async_listen("owm_precipitation_forecast_api_error", capture_event)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            side_effect=OWMApiKeyError("Invalid key"),
        ):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

        # Error event should be fired
        assert len(events) > 0
        assert "error" in events[0].data
