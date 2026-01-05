from homeassistant import config_entries
from homeassistant.data_entry_flow import RESULT_TYPE_FORM, RESULT_TYPE_CREATE_ENTRY
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_owm_precipitation_forecast.const import DOMAIN, CONF_API_KEY, CONF_LOCATION_NAME, CONF_LATITUDE, CONF_LONGITUDE

async def test_config_flow(hass, aiohttp_mock):
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] == RESULT_TYPE_FORM

    aiohttp_mock.get("https://api.openweathermap.org/data/3.0/onecall", json={"hourly": [], "daily": []})

    user_input = {
        CONF_API_KEY: "test_key",
        CONF_LOCATION_NAME: "Test Location",
        CONF_LATITUDE: 0.0,
        CONF_LONGITUDE: 0.0,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)
    assert result["type"] == RESULT_TYPE_CREATE_ENTRY

# More tests for errors, options, etc.
