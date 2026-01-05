"""Tests for config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from custom_components.ha_owm_precipitation_forecast.config_flow import (
    OWMPrecipitationFlowHandler,
)
from custom_components.ha_owm_precipitation_forecast.const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    DOMAIN,
)


@pytest.mark.asyncio
async def test_user_flow(hass: HomeAssistant, config_data):
    """Test successful user flow."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.config_flow.OWMWeatherService"
    ) as mock_service_class:
        mock_service = AsyncMock()
        mock_service.async_get_forecast = AsyncMock(
            return_value={"current": {"dt": 123}}
        )
        mock_service_class.return_value = mock_service

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data=config_data,
        )

        assert result["type"] == "create_entry"
        assert result["title"] == "New York"
        assert result["data"] == config_data


@pytest.mark.asyncio
async def test_invalid_api_key(hass: HomeAssistant, config_data):
    """Test flow with invalid API key."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.config_flow.OWMWeatherService"
    ) as mock_service_class:
        mock_service = AsyncMock()
        mock_service.async_get_forecast = AsyncMock(
            side_effect=ValueError("Invalid API key")
        )
        mock_service_class.return_value = mock_service

        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data=config_data,
        )

        assert result["type"] == "form"
        assert "invalid_auth" in result["errors"].get("base", "")


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant, config_data):
    """Test options flow."""
    entry = await hass.config_entries.async_add(
        config_data=config_data,
        domain=DOMAIN,
        title="Test",
    )

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["step_id"] == "init"
