"""Integration tests for config flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from custom_components.owm_precipitation_forecast.const import (
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    CONF_POLLING_INTERVAL,
    DOMAIN,
    ERROR_API_KEY_INVALID,
    ERROR_LOCATION_INVALID,
    POLLING_INTERVALS,
)


@pytest.mark.integration
class TestConfigFlow:
    """Test the config flow."""

    async def test_user_flow_success(self, hass: HomeAssistant, mock_owm_response):
        """Test successful user flow."""
        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            assert result["type"] == data_entry_flow.FlowResultType.FORM
            assert result["step_id"] == "user"

            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={
                    CONF_API_KEY: "test_api_key",
                    CONF_LOCATION_NAME: "Test Location",
                    CONF_LATITUDE: 45.0,
                    CONF_LONGITUDE: -93.0,
                    CONF_ENABLE_RAIN: True,
                    CONF_ENABLE_SNOW: True,
                    "polling_interval_option": "1_hour",
                },
            )

            assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
            assert result["title"] == "Test Location"
            assert result["data"][CONF_API_KEY] == "test_api_key"
            assert result["data"][CONF_LATITUDE] == 45.0

    async def test_user_flow_invalid_api_key(self, hass: HomeAssistant):
        """Test user flow with invalid API key."""
        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            side_effect=Exception("API key invalid"),
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={
                    CONF_API_KEY: "invalid_key",
                    CONF_LOCATION_NAME: "Test",
                    CONF_LATITUDE: 45.0,
                    CONF_LONGITUDE: -93.0,
                    CONF_ENABLE_RAIN: True,
                    CONF_ENABLE_SNOW: True,
                    "polling_interval_option": "1_hour",
                },
            )

            assert result["type"] == data_entry_flow.FlowResultType.FORM
            assert result["errors"]["base"] == ERROR_API_KEY_INVALID

    async def test_user_flow_invalid_coordinates(self, hass: HomeAssistant):
        """Test user flow with invalid coordinates."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={
                CONF_API_KEY: "test_key",
                CONF_LOCATION_NAME: "Test",
                CONF_LATITUDE: 100.0,  # Invalid
                CONF_LONGITUDE: -93.0,
                CONF_ENABLE_RAIN: True,
                CONF_ENABLE_SNOW: True,
                "polling_interval_option": "1_hour",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["errors"]["base"] == ERROR_LOCATION_INVALID

    async def test_user_flow_duplicate_location(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test user flow with duplicate location."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            result = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                user_input={
                    CONF_API_KEY: "test_key",
                    CONF_LOCATION_NAME: "Different Name",
                    CONF_LATITUDE: 45.0,  # Same as mock_config_entry
                    CONF_LONGITUDE: -93.0,  # Same as mock_config_entry
                    CONF_ENABLE_RAIN: True,
                    CONF_ENABLE_SNOW: True,
                    "polling_interval_option": "1_hour",
                },
            )

            assert result["type"] == data_entry_flow.FlowResultType.ABORT
            assert result["reason"] == "already_configured"


@pytest.mark.integration
class TestOptionsFlow:
    """Test the options flow."""

    async def test_options_flow(self, hass: HomeAssistant, mock_config_entry):
        """Test options flow."""
        mock_config_entry.add_to_hass(hass)

        result = await hass.config_entries.options.async_init(
            mock_config_entry.entry_id
        )

        assert result["type"] == data_entry_flow.FlowResultType.FORM
        assert result["step_id"] == "init"

        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_ENABLE_RAIN: False,
                CONF_ENABLE_SNOW: True,
                "polling_interval_option": "4_hours",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_ENABLE_RAIN] is False
        assert result["data"][CONF_ENABLE_SNOW] is True
        assert result["data"][CONF_POLLING_INTERVAL] == POLLING_INTERVALS["4_hours"]

    async def test_options_flow_toggle_sensors(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test toggling sensors in options flow."""
        mock_config_entry.add_to_hass(hass)

        # Start with both enabled
        assert mock_config_entry.options[CONF_ENABLE_RAIN] is True
        assert mock_config_entry.options[CONF_ENABLE_SNOW] is True

        result = await hass.config_entries.options.async_init(
            mock_config_entry.entry_id
        )

        # Disable rain, keep snow
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_ENABLE_RAIN: False,
                CONF_ENABLE_SNOW: True,
                "polling_interval_option": "1_hour",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_ENABLE_RAIN] is False
        assert result["data"][CONF_ENABLE_SNOW] is True

    async def test_options_flow_change_polling_interval(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test changing polling interval."""
        mock_config_entry.add_to_hass(hass)

        result = await hass.config_entries.options.async_init(
            mock_config_entry.entry_id
        )

        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_ENABLE_RAIN: True,
                CONF_ENABLE_SNOW: True,
                "polling_interval_option": "15_minutes",
            },
        )

        assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_POLLING_INTERVAL] == POLLING_INTERVALS["15_minutes"]
