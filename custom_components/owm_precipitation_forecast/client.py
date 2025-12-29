from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import asyncio
import async_timeout
from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import OWM_ONECALL_URL, OWM_UNITS
from .exceptions import OWMPrecipitationAPIError


@dataclass
class OWMCoordinates:
    latitude: float
    longitude: float


class OWMClient:
    """Async client for OpenWeatherMap One Call API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        coords: OWMCoordinates,
    ) -> None:
        self._hass = hass
        self._api_key = api_key
        self._coords = coords
        # Use HA's shared aiohttp client session
        self._session = async_get_clientsession(hass)

    async def async_get_forecast(self) -> dict[str, Any]:
        """Fetch forecast data from OWM One Call 3.0."""
        params = {
            "lat": self._coords.latitude,
            "lon": self._coords.longitude,
            "appid": self._api_key,
            "units": OWM_UNITS,
            "exclude": "minutely,current,alerts",
        }

        try:
            async with async_timeout.timeout(20):
                async with self._session.get(OWM_ONECALL_URL, params=params) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise OWMPrecipitationAPIError(
                            f"OWM API error {resp.status}: {text}"
                        )
                    data = await resp.json()
        except (ClientError, asyncio.TimeoutError) as exc:
            raise OWMPrecipitationAPIError(
                f"OWM network error: {exc}"
            ) from exc

        if "hourly" not in data or "daily" not in data:
            raise OWMPrecipitationAPIError("Missing hourly/daily in OWM response")

        return data
