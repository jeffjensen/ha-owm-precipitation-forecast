"""OpenWeatherMap API client."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientTimeout

from .const import LOGGER_NAME, OWM_API_ENDPOINT, OWM_API_TIMEOUT

_LOGGER = logging.getLogger(LOGGER_NAME)


class OpenWeatherMapError(Exception):
    """Base exception for OWM errors."""


class OpenWeatherMapClient:
    """Client for OpenWeatherMap API."""

    def __init__(self, api_key: str, latitude: float, longitude: float) -> None:
        """Initialize the client."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=ClientTimeout(total=OWM_API_TIMEOUT)
            )
        return self._session

    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def validate_credentials(self) -> None:
        """Validate API credentials."""
        try:
            await self.get_forecast_data()
        except OpenWeatherMapError:
            raise
        except Exception as err:
            _LOGGER.error("Validation error: %s", err)
            raise OpenWeatherMapError("Failed to validate credentials") from err

    async def get_forecast_data(self) -> dict[str, Any]:
        """Fetch forecast data from API."""
        session = await self._get_session()
        
        params = {
            "lat": self.latitude,
            "lon": self.longitude,
            "appid": self.api_key,
            "units": "imperial",  # Use imperial for Fahrenheit
            "exclude": "current,minutely,alerts",  # Only need hourly and daily
        }

        try:
            _LOGGER.debug("Fetching forecast data from OWM API")
            async with session.get(OWM_API_ENDPOINT, params=params) as response:
                if response.status == 401:
                    raise OpenWeatherMapError("Invalid API key")
                elif response.status == 429:
                    raise OpenWeatherMapError("API rate limit exceeded")
                elif response.status != 200:
                    raise OpenWeatherMapError(
                        f"API returned status {response.status}"
                    )

                data = await response.json()
                _LOGGER.debug("Successfully fetched forecast data")
                return self._process_forecast_data(data)

        except ClientError as err:
            _LOGGER.error("Connection error: %s", err)
            raise OpenWeatherMapError(f"Connection error: {err}") from err
        except asyncio.TimeoutError as err:
            _LOGGER.error("Request timeout")
            raise OpenWeatherMapError("Request timeout") from err

    def _process_forecast_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Process raw API data into structured format."""
        processed = {
            "hourly": [],
            "daily": [],
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "timezone": raw_data.get("timezone", "UTC"),
            },
        }

        # Process hourly data
        for hour in raw_data.get("hourly", [])[:48]:  # Next 48 hours
            processed["hourly"].append({
                "timestamp": datetime.fromtimestamp(
                    hour["dt"], tz=timezone.utc
                ).isoformat(),
                "temperature": hour["temp"],
                "rain": hour.get("rain", {}).get("1h", 0.0),  # mm
                "snow": hour.get("snow", {}).get("1h", 0.0),  # mm
            })

        # Process daily data
        for day in raw_data.get("daily", [])[:7]:  # Next 7 days
            processed["daily"].append({
                "timestamp": datetime.fromtimestamp(
                    day["dt"], tz=timezone.utc
                ).isoformat(),
                "temperature": day.get("temp", {}).get("day", 0.0),
                "rain": day.get("rain", 0.0),  # mm
                "snow": day.get("snow", 0.0),  # mm
            })

        return processed
