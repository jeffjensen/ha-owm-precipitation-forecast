"""Test config flow."""
import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ha_owm_precipitation_forecast.const import (
    CONF_API_KEY,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    CONF_POLL_INTERVAL,
    DEFAULT_LOCATION_NAME,
    DOMAIN,
)


async def test_form_display(hass: HomeAssistant) -> None:
    """Test that the form is displayed correctly."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_form_fields(hass: HomeAssistant) -> None:
    """Test form contains expected fields."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    schema = result["data_schema"].schema
    assert CONF_API_KEY in str(schema)
    assert CONF_LATITUDE in str(schema)
    assert CONF_LONGITUDE in str(schema)


async def test_options_flow(hass: HomeAssistant) -> None:
    """Test options flow."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test",
        data={
            CONF_API_KEY: "test_key",
            CONF_LATITUDE: 40.0,
            CONF_LONGITUDE: -74.0,
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"


async def test_options_flow_fields(hass: HomeAssistant) -> None:
    """Test options flow contains expected fields."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test",
        data={
            CONF_API_KEY: "test_key",
            CONF_LATITUDE: 40.0,
            CONF_LONGITUDE: -74.0,
        },
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    schema = result["data_schema"].schema
    assert CONF_ENABLE_RAIN in str(schema)
    assert CONF_ENABLE_SNOW in str(schema)
    assert CONF_POLL_INTERVAL in str(schema)
