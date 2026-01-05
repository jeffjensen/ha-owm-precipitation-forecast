"""Tests for data coordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from custom_components.ha_owm_precipitation_forecast.coordinator import (
    OWMPrecipitationCoordinator,
)


@pytest.mark.asyncio
async def test_coordinator_initialization(hass, config_data, mock_owm_response):
    """Test coordinator initialization."""
    entry = AsyncMock()
    entry.data = config_data
    entry.entry_id = "test"

    with patch(
        "custom_components.ha_owm_precipitation_forecast.coordinator.OWMWeatherService"
    ):
        coordinator = OWMPrecipitationCoordinator(hass, entry)

        assert coordinator.latitude == config_data["latitude"]
        assert coordinator.longitude == config_data["longitude"]
        assert coordinator.last_error is None


@pytest.mark.asyncio
async def test_coordinator_data_update(hass, config_data, mock_owm_response):
    """Test data update."""
    entry = AsyncMock()
    entry.data = config_data
    entry.entry_id = "test"

    with patch(
        "custom_components.ha_owm_precipitation_forecast.coordinator.OWMWeatherService"
    ) as mock_service_class:
        mock_service = AsyncMock()
        mock_service.async_get_forecast = AsyncMock(return_value=mock_owm_response)
        mock_service_class.return_value = mock_service

        coordinator = OWMPrecipitationCoordinator(hass, entry)

        with patch.object(
            coordinator.weather_service,
            "async_get_forecast",
            mock_service.async_get_forecast,
        ):
            data = await coordinator._async_update_data()

        assert "hourly" in data
        assert "daily" in data
        assert "next24h" in data
        assert len(data["hourly"]) <= 24


@pytest.mark.asyncio
async def test_coordinator_error_handling(hass, config_data):
    """Test error handling."""
    entry = AsyncMock()
    entry.data = config_data
    entry.entry_id = "test"

    with patch(
        "custom_components.ha_owm_precipitation_forecast.coordinator.OWMWeatherService"
    ) as mock_service_class:
        mock_service = AsyncMock()
        mock_service.async_get_forecast = AsyncMock(side_effect=Exception("API Error"))
        mock_service_class.return_value = mock_service

        coordinator = OWMPrecipitationCoordinator(hass, entry)

        with patch.object(
            coordinator.weather_service,
            "async_get_forecast",
            mock_service.async_get_forecast,
        ):
            with pytest.raises(Exception):
                await coordinator._async_update_data()

        assert coordinator.last_error is not None
