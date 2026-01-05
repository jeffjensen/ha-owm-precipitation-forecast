import logging
from datetime import timedelta
import json
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp

from .const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_POLL_INTERVAL,
    CONF_SNOW_RATIOS,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_SNOW_RATIOS,
    OWM_API_URL,
    POLL_INTERVALS,
    UNIT_INCHES,
)

_LOGGER = logging.getLogger(__name__)

class OWMPrecipForecastCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, session: aiohttp.ClientSession) -> None:
        self.entry = entry
        self.session = session
        update_interval = timedelta(seconds=entry.options.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL))
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> dict[str, Any]:
        params = {
            "lat": self.entry.data[CONF_LATITUDE],
            "lon": self.entry.data[CONF_LONGITUDE],
            "appid": self.entry.data[CONF_API_KEY],
            "exclude": "current,minutely,alerts",
            "units": "imperial",
        }
        try:
            async with self.session.get(OWM_API_URL, params=params) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"OWM API error: {resp.status}")
                data = await resp.json()
            return self._process_data(data)
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error fetching OWM data: {err}") from err

    def _process_data(self, data: dict) -> dict:
        enable_rain = self.entry.options.get(CONF_ENABLE_RAIN, True)
        enable_snow = self.entry.options.get(CONF_ENABLE_SNOW, True)
        snow_ratios_str = self.entry.options.get(CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS)
        snow_ratios = self._parse_snow_ratios(snow_ratios_str)

        hourly = []
        if "hourly" in data:
            for h in data["hourly"]:
                temp = h.get("temp", 0)
                rain_mm = h.get("rain", {}).get("1h", 0)
                snow_mm = h.get("snow", {}).get("1h", 0)
                rain_in = rain_mm / 25.4 if enable_rain else 0
                snow_in = (snow_mm / 25.4) * self._get_snow_ratio(temp, snow_ratios) if enable_snow else 0
                hourly.append({
                    "dt": h["dt"],
                    "rain": rain_in,
                    "snow": snow_in,
                })

        daily = []
        if "daily" in data:
            for d in data["daily"]:
                avg_temp = (d["temp"]["min"] + d["temp"]["max"]) / 2
                rain_mm = d.get("rain", 0)
                snow_mm = d.get("snow", 0)
                rain_in = rain_mm / 25.4 if enable_rain else 0
                snow_in = (snow_mm / 25.4) * self._get_snow_ratio(avg_temp, snow_ratios) if enable_snow else 0
                daily.append({
                    "dt": d["dt"],
                    "rain": rain_in,
                    "snow": snow_in,
                })

        next24h_rain = sum(h["rain"] for h in hourly[:24]) if enable_rain else 0
        next24h_snow = sum(h["snow"] for h in hourly[:24]) if enable_snow else 0

        return {
            "hourly": hourly,
            "daily": daily,
            "next24h_rain": next24h_rain,
            "next24h_snow": next24h_snow,
            "health": "ok" if hourly or daily else "error",
        }

    def _parse_snow_ratios(self, ratios_str: str) -> list[tuple[float, float, float]]:
        ratios = []
        for part in ratios_str.split(","):
            min_t, max_t, ratio = part.strip().split(":")
            min_t = float("-inf") if min_t == "-inf" else float(min_t)
            max_t = float("inf") if max_t == "inf" else float(max_t)
            ratios.append((min_t, max_t, float(ratio)))
        return ratios

    def _get_snow_ratio(self, temp: float, ratios: list[tuple[float, float, float]]) -> float:
        for min_t, max_t, ratio in ratios:
            if min_t <= temp < max_t:
                return ratio
        return 10.0  # default
