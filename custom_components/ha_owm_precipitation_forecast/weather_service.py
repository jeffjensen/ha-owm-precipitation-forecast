"""OpenWeatherMap API service."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_TIMEOUT,
    LOGGER,
)

_LOGGER: logging.Logger = LOGGER


class OWMWeatherService:
    """Service for interacting with OpenWeatherMap API."""

    def __init__(self, api_key: str, session: AsyncClientSession) -> None:
        """Initialize the service."""
        self.api_key = api_key
        self.session = session
        self.base_url = "https://api.openweathermap.org/data/3.0"

    async def async_get_forecast(self, lat: float, lon: float) -> dict[str, Any]:
        """Get forecast data from OpenWeatherMap One Call API 3.0."""
        url = f"{self.base_url}/onecall"

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }

        try:
            async with self.session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
            ) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    raise ValueError("Invalid API key")
                elif response.status == 404:
                    raise ValueError("Location not found")
                else:
                    raise Exception(
                        f"API returned status {response.status}: "
                        f"{await response.text()}"
                    )
        except asyncio.TimeoutError as ex:
            raise TimeoutError("Request to OpenWeatherMap API timed out") from ex
        except aiohttp.ClientError as ex:
            raise Exception(f"Network error: {ex}") from ex


import asyncio
