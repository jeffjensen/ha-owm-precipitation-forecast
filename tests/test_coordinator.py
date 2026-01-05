import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import mock_config_entry_setup

from custom_components.ha_owm_precipitation_forecast.coordinator import OWMPrecipForecastCoordinator
from custom_components.ha_owm_precipitation_forecast.const import DOMAIN

@pytest.mark.asyncio
async def test_coordinator_update(hass: HomeAssistant, aiohttp_mock):
    entry = MockConfigEntry(domain=DOMAIN, data={"api_key": "key", "latitude": 0, "longitude": 0}, options={})
    aiohttp_mock.get("https://api.openweathermap.org/data/3.0/onecall", json={
        "hourly": [{"dt": 0, "temp": 20, "rain": {"1h": 25.4}, "snow": {"1h": 25.4}}],
        "daily": [{"dt": 0, "temp": {"min": 10, "max": 30}, "rain": 25.4, "snow": 25.4}],
    })
    coordinator = OWMPrecipForecastCoordinator(hass, entry, hass.http.client_session)
    await coordinator.async_refresh()
    data = coordinator.data
    assert data["next24h_rain"] == pytest.approx(1.0)
    assert data["next24h_snow"] == pytest.approx(10.0)  # default ratio 10

# More tests for different ratios, errors, etc.
