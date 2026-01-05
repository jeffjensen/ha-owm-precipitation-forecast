"""Data coordinator for OWM Precipitation Forecast."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    NAME,
    LOGGER,
    SCAN_INTERVALS,
    MAX_RETRIES,
    RETRY_DELAY,
)
from .weather_service import OWMWeatherService
from .snow_calculator import SnowCalculator

_LOGGER: logging.Logger = LOGGER


class OWMPrecipitationCoordinator(DataUpdateCoordinator):
    """Coordinator for updating OWM precipitation forecast data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.entry = entry

        scan_interval_minutes = SCAN_INTERVALS.get(
            str(entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
            DEFAULT_SCAN_INTERVAL,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=NAME,
            update_interval=timedelta(minutes=scan_interval_minutes),
        )

        session = async_get_clientsession(hass)
        self.weather_service = OWMWeatherService(
            api_key=entry.data[CONF_API_KEY],
            session=session,
        )

        self.snow_calculator = SnowCalculator(
            base_ratio=entry.data.get("snow_ratio", 10.0),
            use_temp_adjusted=entry.data.get("temperature_adjusted_ratio", True),
        )

        self.latitude = entry.data[CONF_LATITUDE]
        self.longitude = entry.data[CONF_LONGITUDE]
        self.last_error: str | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from OWM API."""
        try:
            forecast = await self.weather_service.async_get_forecast(
                lat=self.latitude,
                lon=self.longitude,
            )

            self.last_error = None
            return self._process_forecast(forecast)

        except Exception as ex:
            self.last_error = str(ex)
            _LOGGER.error(
                "Error fetching data from OpenWeatherMap: %s",
                ex,
            )
            raise UpdateFailed(f"Failed to fetch data: {ex}") from ex

    def _process_forecast(self, forecast: dict[str, Any]) -> dict[str, Any]:
        """Process raw forecast data."""
        processed = {
            "hourly": [],
            "daily": [],
            "next24h": {"rain": 0.0, "snow": 0.0},
            "last_update": None,
        }

        # Process hourly data
        if "hourly" in forecast:
            hourly_rain_sum = 0.0
            hourly_snow_sum = 0.0

            for i, hour in enumerate(forecast["hourly"][:24]):
                rain = hour.get("rain", {}).get("1h", 0.0) * 0.0393701  # mm to inches
                snow = hour.get("snow", {}).get("1h", 0.0) * 0.0393701

                hourly_rain_sum += rain
                hourly_snow_sum += snow

                processed["hourly"].append(
                    {
                        "timestamp": hour.get("dt"),
                        "rain": rain,
                        "snow": snow,
                        "temperature": hour.get("temp"),
                    }
                )

            processed["next24h"]["rain"] = hourly_rain_sum
            processed["next24h"]["snow"] = hourly_snow_sum

        # Process daily data
        if "daily" in forecast:
            for day in forecast["daily"][:8]:
                rain = day.get("rain", 0.0) * 0.0393701  # mm to inches
                snow = day.get("snow", 0.0) * 0.0393701

                # Apply snow ratio if needed
                if snow == 0 and rain > 0:
                    temp = day.get("temp", {}).get("day", 0)
                    snow = self.snow_calculator.calculate_snow(rain, temp)

                processed["daily"].append(
                    {
                        "timestamp": day.get("dt"),
                        "rain": rain,
                        "snow": snow,
                        "temperature": day.get("temp", {}).get("day"),
                    }
                )

        processed["last_update"] = forecast.get("current", {}).get("dt")

        return processed
