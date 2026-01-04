# Handles all API communication with OpenWeatherMap
# Implements robust error handling
# Manages HTTP session lifecycle
# Provides typed error codes for different failure modes

"""OpenWeatherMap API client."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import (
    ERROR_API_KEY_INVALID,
    ERROR_API_UNAVAILABLE,
    ERROR_RATE_LIMITED,
    ERROR_UNKNOWN,
    OWM_API_TIMEOUT,
    OWM_API_URL,
)

_LOGGER = logging.getLogger(__name__)


class OWMClientError(Exception):
    """Base exception for OWM client errors."""

    def __init__(self, message: str, error_code: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.error_code = error_code


class OWMClient:
    """Client for OpenWeatherMap API."""

    def __init__(
        self,
        api_key: str,
        latitude: float,
        longitude: float,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the client."""
        self._api_key = api_key
        self._latitude = latitude
        self._longitude = longitude
        self._session = session
        self._own_session = session is None

    async def async_get_forecast(self) -> dict[str, Any]:
        """Get forecast data from OpenWeatherMap."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        params = {
            "lat": self._latitude,
            "lon": self._longitude,
            "appid": self._api_key,
            "units": "imperial",  # Get temperature in Fahrenheit
            "exclude": "current,minutely,alerts",  # We only need hourly and daily
        }

        try:
            async with asyncio.timeout(OWM_API_TIMEOUT):
                async with self._session.get(OWM_API_URL, params=params) as response:
                    if response.status == 401:
                        raise OWMClientError(
                            "Invalid API key",
                            ERROR_API_KEY_INVALID,
                        )
                    elif response.status == 429:
                        raise OWMClientError(
                            "API rate limit exceeded",
                            ERROR_RATE_LIMITED,
                        )
                    elif response.status != 200:
                        raise OWMClientError(
                            f"API returned status {response.status}",
                            ERROR_API_UNAVAILABLE,
                        )

                    data = await response.json()
                    _LOGGER.debug("Successfully retrieved forecast data")
                    return data

        except asyncio.TimeoutError as err:
            raise OWMClientError(
                "Request timeout",
                ERROR_API_UNAVAILABLE,
            ) from err
        except aiohttp.ClientError as err:
            raise OWMClientError(
                f"Client error: {err}",
                ERROR_API_UNAVAILABLE,
            ) from err
        except Exception as err:
            _LOGGER.exception("Unexpected error fetching forecast")
            raise OWMClientError(
                f"Unexpected error: {err}",
                ERROR_UNKNOWN,
            ) from err

    async def async_close(self) -> None:
        """Close the session if we own it."""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None
