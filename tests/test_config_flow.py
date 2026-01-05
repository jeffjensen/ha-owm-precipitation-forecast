"""Tests for config_flow.py."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.ha_owm_precipitation_forecast.const import DOMAIN


@pytest.mark.asyncio
async def test_form_user(hass: HomeAssistant):
    """Test user config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result["errors"] == {}


@pytest.mark.asyncio
async def test_form_user_success(hass: HomeAssistant, mock_owm_client):
    """Test successful user config."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.config_flow.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "location_name": "Test",
                "latitude": 44.9778,
                "longitude": -93.2650,
                "api_key": "test_key",
                "enable_rain": True,
                "enable_snow": True,
                "update_interval": "60",
            },
        )

        assert result2["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result2["title"] == "Location (44.9778, -93.265)"
        assert result2["data"]["location_name"] == "Test"


@pytest.mark.asyncio
async def test_form_invalid_coordinates(hass: HomeAssistant):
    """Test invalid coordinates."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "location_name": "Test",
            "latitude": 100,  # Invalid
            "longitude": -93.2650,
            "api_key": "test_key",
            "enable_rain": True,
            "enable_snow": True,
            "update_interval": "60",
        },
    )

    assert result2["type"] == data_entry_flow.RESULT_TYPE_FORM
    assert result2["errors"] == {"base": "invalid_coordinates"}


@pytest.mark.asyncio
async def test_form_invalid_api_key(hass: HomeAssistant, mock_owm_client):
    """Test invalid API key."""
    mock_owm_client.validate_credentials.side_effect = Exception("Invalid API key")

    with patch(
        "custom_components.ha_owm_precipitation_forecast.config_flow.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "location_name": "Test",
                "latitude": 44.9778,
                "longitude": -93.2650,
                "api_key": "bad_key",
                "enable_rain": True,
                "enable_snow": True,
                "update_interval": "60",
            },
        )

        assert result2["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result2["errors"] == {"base": "invalid_api_key"}


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant, mock_config_entry, mock_owm_client):
    """Test options flow."""
    with patch(
        "custom_components.ha_owm_precipitation_forecast.OpenWeatherMapClient",
        return_value=mock_owm_client,
    ):
        mock_config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        result = await hass.config_entries.options.async_init(
            mock_config_entry.entry_id
        )

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "init"

        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                "enable_rain": False,
                "enable_snow": True,
                "update_interval": "240",
            },
        )

        assert result2["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert mock_config_entry.options == {
            "enable_rain": False,
            "enable_snow": True,
            "update_interval": "240",
        }
