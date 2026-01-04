"""Test data coordinator."""
import pytest
from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_owm_precipitation_forecast.const import (
    DOMAIN,
    HEALTH_ERROR,
    HEALTH_OK,
    HEALTH_WARNING,
    OWM_API_URL,
)
from custom_components.ha_owm_precipitation_forecast.coordinator import (
    OWMPrecipitationCoordinator,
)


@pytest.mark.asyncio
async def test_coordinator_initialization(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test coordinator initialization."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

    assert coordinator.health_status == HEALTH_OK
    assert coordinator.health_message == "Operating normally"
    assert coordinator._consecutive_errors == 0


@pytest.mark.asyncio
async def test_coordinator_successful_update(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_forecast_data: dict,
) -> None:
    """Test successful data update."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

    with aioresponses() as mock:
        mock.get(OWM_API_URL, payload=mock_forecast_data, status=200)

        await coordinator.async_refresh()

        assert coordinator.data is not None
        assert "hourly_rain" in coordinator.data
        assert coordinator.health_status == HEALTH_OK


@pytest.mark.asyncio
async def test_coordinator_error_handling(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test coordinator error handling."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

    with aioresponses() as mock:
        # Simulate API error
        mock.get(OWM_API_URL, status=500)

        with pytest.raises(UpdateFailed):
            await coordinator.async_refresh()

        assert coordinator._consecutive_errors == 1
        assert coordinator.health_status == HEALTH_WARNING


@pytest.mark.asyncio
async def test_coordinator_multiple_errors(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test coordinator handles multiple consecutive errors."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

    with aioresponses() as mock:
        # Simulate multiple errors
        for _ in range(3):
            mock.get(OWM_API_URL, status=500)

        # First two errors - should be warning
        with pytest.raises(UpdateFailed):
            await coordinator.async_refresh()
        assert coordinator.health_status == HEALTH_WARNING

        with pytest.raises(UpdateFailed):
            await coordinator.async_refresh()
        assert coordinator.health_status == HEALTH_WARNING

        # Third error - should escalate to error
        with pytest.raises(UpdateFailed):
            await coordinator.async_refresh()
        assert coordinator.health_status == HEALTH_ERROR
        assert coordinator._consecutive_errors == 3


@pytest.mark.asyncio
async def test_coordinator_recovery(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_forecast_data: dict,
) -> None:
    """Test coordinator recovers after errors."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

    with aioresponses() as mock:
        # First request fails
        mock.get(OWM_API_URL, status=500)
        with pytest.raises(UpdateFailed):
            await coordinator.async_refresh()

        assert coordinator._consecutive_errors == 1

        # Second request succeeds
        mock.get(OWM_API_URL, payload=mock_forecast_data, status=200)
        await coordinator.async_refresh()

        # Should reset error counter
        assert coordinator._consecutive_errors == 0
        assert coordinator.health_status == HEALTH_OK


@pytest.mark.asyncio
async def test_coordinator_poll_interval_update(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test updating poll interval."""
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)

    original_interval = coordinator.update_interval

    coordinator.update_poll_interval(120)

    assert coordinator.update_interval.total_seconds() == 7200  # 120 minutes
    assert coordinator.update_interval != original_interval
