"""Advanced scenario tests for complex real-world cases."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.owm_precipitation_forecast.const import (
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
    OWMApiError,
    OWMApiRateLimitError,
    OWMApiTimeoutError,
)


@pytest.mark.advanced
class TestRateLimiting:
    """Test rate limiting scenarios."""

    async def test_rate_limit_warning_threshold(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test rate limit warning at 80% threshold."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        
        # Set API calls to 800 (80% of 1000)
        coordinator.api_stats.total_calls_today = 800

        # Should trigger throttle check
        assert coordinator._should_throttle()
        assert coordinator.health_status.status == HEALTH_STATUS_OK

    async def test_rate_limit_enforcement(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test rate limit enforcement at 100%."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        
        # Set API calls to limit
        coordinator.api_stats.total_calls_today = OWM_RATE_LIMIT_CALLS

        # Should throttle
        assert coordinator._should_throttle()

    async def test_daily_counter_reset(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test daily counter resets after 24 hours."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        
        coordinator.api_stats.total_calls_today = 500
        coordinator.api_stats.last_call_time = datetime.now() - timedelta(days=2)

        # Trigger reset check
        coordinator._update_api_calls_tracking()

        # Counter should be reset
        assert coordinator.api_stats.total_calls_today == 0


@pytest.mark.advanced
class TestNetworkResilience:
    """Test network resilience and error recovery."""

    async def test_intermittent_network_failure(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test recovery from intermittent network failures."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        
        call_count = 0

        async def mock_get_forecast(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OWMApiConnectionError("Network error")
            return mock_owm_response

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            side_effect=mock_get_forecast,
        ):
            with patch("asyncio.sleep", return_value=None):
                data = await coordinator._async_update_data()
                
                # Should succeed after retries
                assert data is not None
                assert call_count == 3

    async def test_persistent_network_failure(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test handling of persistent network failures."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            side_effect=OWMApiConnectionError("Network error"),
        ):
            with pytest.raises(Exception):  # UpdateFailed
                await coordinator._async_update_data()

            # Health should show error
            assert coordinator.health_status.status == HEALTH_STATUS_ERROR
            assert coordinator.health_status.error_count > 0

    async def test_timeout_recovery(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test recovery from timeout errors."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
        
        call_count = 0

        async def mock_get_forecast(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OWMApiTimeoutError("Timeout")
            return mock_owm_response

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            side_effect=mock_get_forecast,
        ):
            with patch("asyncio.sleep", return_value=None):
                data = await coordinator._async_update_data()
                
                assert data is not None
                assert call_count == 2


@pytest.mark.advanced
class TestComplexWeatherScenarios:
    """Test complex weather scenarios."""

    async def test_mixed_precipitation_scenario(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test mixed rain and snow precipitation."""
        # Create data with temperatures around freezing
        mixed_response = {
            "lat": 45.0,
            "lon": -93.0,
            "timezone": "America/Chicago",
            "hourly": [
                {
                    "dt": int(datetime.now().timestamp()),
                    "temp": 0,  # 32°F - freezing point
                    "rain": {"1h": 2.54},
                    "snow": {"1h": 2.54},
                    "pop": 0.9,
                }
            ],
            "daily": [
                {
                    "dt": int(datetime.now().timestamp()),
                    "temp": {"max": 2, "min": -2},
                    "rain": 12.7,
                    "snow": 12.7,
                    "pop": 0.8,
                }
            ],
        }

        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mixed_response,
        ):
            data = await coordinator._async_update_data()
            
            assert data is not None
            # Should have both rain and snow data
            assert len(data.hourly_forecasts) > 0
            assert len(data.daily_forecasts) > 0

    async def test_extreme_snowfall_scenario(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response_heavy_snow
    ):
        """Test extreme snowfall scenario."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response_heavy_snow,
        ):
            data = await coordinator._async_update_data()
            
            assert data is not None
            # Verify heavy snow calculations
            total_snow = data.get_hourly_snow_total(24)
            assert total_snow > 0

    async def test_no_precipitation_scenario(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response_no_precipitation
    ):
        """Test scenario with no precipitation."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response_no_precipitation,
        ):
            data = await coordinator._async_update_data()
            
            assert data is not None
            # All totals should be zero
            assert data.get_hourly_rain_total(24) == 0.0
            assert data.get_hourly_snow_total(24) == 0.0


@pytest.mark.advanced
class TestErrorAccumulation:
    """Test error accumulation and recovery."""

    async def test_error_counter_accumulation(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test error counter accumulates correctly."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        # Simulate multiple errors
        for _ in range(5):
            coordinator.api_stats.increment_errors("Test error")

        assert coordinator.api_stats.error_count == 5
        assert coordinator.health_status.error_count == 5

    async def test_error_clearing(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test error clearing functionality."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        # Add errors
        coordinator.api_stats.increment_errors("Error 1")
        coordinator.api_stats.increment_errors("Error 2")
        
        assert coordinator.api_stats.error_count == 2

        # Clear errors
        coordinator.clear_errors()

        assert coordinator.api_stats.error_count == 0
        assert coordinator.health_status.status == HEALTH_STATUS_OK

    async def test_health_status_transitions(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test health status transitions."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        # Start OK
        assert coordinator.health_status.status == HEALTH_STATUS_OK

        # Simulate rate limit warning
        coordinator.api_stats.total_calls_today = 850
        coordinator._update_health_status(HEALTH_STATUS_WARNING, "Rate limit warning")
        assert coordinator.health_status.status == HEALTH_STATUS_WARNING

        # Simulate error
        coordinator.api_stats.increment_errors("API error")
        coordinator._update_health_status(HEALTH_STATUS_ERROR, "API error")
        assert coordinator.health_status.status == HEALTH_STATUS_ERROR

        # Recover
        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            await coordinator._async_update_data()
            assert coordinator.health_status.status == HEALTH_STATUS_OK


@pytest.mark.advanced
class TestMultipleLocations:
    """Test scenarios with multiple configured locations."""

    async def test_multiple_coordinators_independent(
        self, hass: HomeAssistant, mock_owm_response
    ):
        """Test multiple coordinators operate independently."""
        from pytest_homeassistant_custom_component.common import MockConfigEntry

        # Create two config entries
        entry1 = MockConfigEntry(
            domain="owm_precipitation_forecast",
            data={
                "api_key": "key1",
                "location_name": "Location 1",
                "latitude": 45.0,
                "longitude": -93.0,
            },
        )

        entry2 = MockConfigEntry(
            domain="owm_precipitation_forecast",
            data={
                "api_key": "key2",
                "location_name": "Location 2",
                "latitude": 40.0,
                "longitude": -75.0,
            },
        )

        coordinator1 = OWMPrecipitationCoordinator(hass, entry1)
        coordinator2 = OWMPrecipitationCoordinator(hass, entry2)

        # Update coordinator1
        with patch.object(
            coordinator1.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            data1 = await coordinator1._async_update_data()

        # coordinator2 should not be affected
        assert coordinator2.data is None

        # Update coordinator2
        with patch.object(
            coordinator2.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            data2 = await coordinator2._async_update_data()

        # Both should have independent data
        assert data1 is not None
        assert data2 is not None
        assert coordinator1.location_name != coordinator2.location_name


@pytest.mark.advanced
class TestDataConsistency:
    """Test data consistency across updates."""

    async def test_data_consistency_across_updates(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test data remains consistent across multiple updates."""
        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=mock_owm_response,
        ):
            # First update
            data1 = await coordinator._async_update_data()
            hourly_count1 = len(data1.hourly_forecasts)
            
            # Second update
            data2 = await coordinator._async_update_data()
            hourly_count2 = len(data2.hourly_forecasts)

            # Should have same structure
            assert hourly_count1 == hourly_count2

    async def test_partial_data_handling(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test handling of partial data responses."""
        # Response with only hourly data
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

        coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

        with patch.object(
            coordinator.api_client,
            "get_forecast",
            return_value=partial_response,
        ):
            data = await coordinator._async_update_data()
            
            # Should handle missing daily data gracefully
            assert data is not None
            assert len(data.hourly_forecasts) > 0
            assert len(data.daily_forecasts) == 0
