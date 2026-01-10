"""OWM Precipitation Forecast integration."""
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

DOMAIN = "owm_precipitation_forecast"
PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
