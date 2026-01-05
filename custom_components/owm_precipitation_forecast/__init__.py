"""The OWM Precipitation Forecast integration."""
import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN, CONF_API_KEY,
    CONF_RATIO_34_PLUS, CONF_RATIO_28_34, CONF_RATIO_20_28,
    CONF_RATIO_10_20, CONF_RATIO_0_10, CONF_RATIO_NEG,
    DEFAULT_RATIO_34_PLUS, DEFAULT_RATIO_28_34, DEFAULT_RATIO_20_28,
    DEFAULT_RATIO_10_20, DEFAULT_RATIO_0_10, DEFAULT_RATIO_NEG
)
from .api import OWMClient
from .coordinator import OWMPrecipitationCoordinator
from .calculator import SnowCalculator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OWM Precipitation Forecast from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    api_key = entry.data[CONF_API_KEY]
    session = async_get_clientsession(hass)
    client = OWMClient(api_key, session)

    # Gather Snow Ratios from Options or Defaults
    opts = entry.options
    ratios = {
        "ratio_34_plus": opts.get(CONF_RATIO_34_PLUS, DEFAULT_RATIO_34_PLUS),
        "ratio_28_34": opts.get(CONF_RATIO_28_34, DEFAULT_RATIO_28_34),
        "ratio_20_28": opts.get(CONF_RATIO_20_28, DEFAULT_RATIO_20_28),
        "ratio_10_20": opts.get(CONF_RATIO_10_20, DEFAULT_RATIO_10_20),
        "ratio_0_10": opts.get(CONF_RATIO_0_10, DEFAULT_RATIO_0_10),
        "ratio_neg": opts.get(CONF_RATIO_NEG, DEFAULT_RATIO_NEG),
    }

    calculator = SnowCalculator(ratios)

    coordinator = OWMPrecipitationCoordinator(hass, client, calculator, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload entry when options change
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)