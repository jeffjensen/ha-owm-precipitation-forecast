"""OpenWeatherMap API client with retry logic and error handling."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    ERROR_API_CONNECTION,
    ERROR_API_KEY_INVALID,
    ERROR_API_RATE_LIMIT,
    ERROR_API_RESPONSE,
    ERROR_API_TIMEOUT,
    OWM_API_BACKOFF_FACTOR,
    OWM_API_BASE_URL,
    OWM_API_MAX_RETRIES,
    OWM_API_RETRY_DELAY,
    OWM_API_TIMEOUT,
)
from .exceptions import (
    OWMApiConnectionError,
    OWMApiError,
    OWMApiKeyError,
    OWMApiRateLimitError,
    OWMApiResponseError,
    OWMApiTimeoutError,
)

_LOGGER = logging.getLogger(__name__)


class OWMApiClient:
    """OpenWeatherMap API client with retry logic."""

    def __init__(self, api_key: str, hass: HomeAssistant) -> None:
        """Initialize the API client."""
        self.api_key = api_key
        self.hass = hass
        self.base_url = OWM_API_BASE_URL
        self.timeout = OWM_API_TIMEOUT
        self.session: aiohttp.ClientSession = async_get_clientsession(hass)
        self._last_call_time: datetime | None = None
        self._call_count = 0

    async def get_forecast(
        self, latitude: float, longitude: float
    ) -> dict[str, Any]:
        """
        Get precipitation forecast for a location.

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location

        Returns:
            Forecast data from OWM API

        Raises:
            OWMApiKeyError: Invalid API key
            OWMApiRateLimitError: Rate limit exceeded
            OWMApiTimeoutError: Request timeout
            OWMApiConnectionError: Connection error
            OWMApiResponseError: Invalid response
            OWMApiError: General API error
        """
        _LOGGER.debug(
            "Fetching forecast for lat=%s, lon=%s", latitude, longitude
        )

        url = self._build_url(latitude, longitude)

        for attempt in range(OWM_API_MAX_RETRIES):
            try:
                data = await self._make_request(url, attempt)
                self._log_successful_call()
                return data

            except OWMApiKeyError:
                # Don't retry on authentication errors
                _LOGGER.error("Invalid API key, not retrying")
                raise

            except OWMApiRateLimitError:
                # Don't retry on rate limit errors
                _LOGGER.error("Rate limit exceeded, not retrying")
                raise

            except (
                OWMApiTimeoutError,
                OWMApiConnectionError,
                OWMApiResponseError,
            ) as err:
                if attempt < OWM_API_MAX_RETRIES - 1:
                    delay = self._calculate_backoff(attempt)
                    _LOGGER.warning(
                        "Request failed (attempt %d/%d): %s. Retrying in %ds",
                        attempt + 1,
                        OWM_API_MAX_RETRIES,
                        err,
                        delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    _LOGGER.error(
                        "Request failed after %d attempts: %s",
                        OWM_API_MAX_RETRIES,
                        err,
                    )
                    raise

        # Should never reach here, but just in case
        raise OWMApiError("Maximum retries exceeded")

    async def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request.

        Returns:
            True if API key is valid

        Raises:
            OWMApiKeyError: Invalid API key
            OWMApiError: Other API errors
        """
        try:
            # Test with a known good location (San Francisco)
            await self.get_forecast(37.7749, -122.4194)
            return True
        except OWMApiKeyError:
            raise
        except Exception as err:
            _LOGGER.error("API key validation failed: %s", err)
            raise OWMApiError(f"API key validation failed: {err}") from err

    def _build_url(self, latitude: float, longitude: float) -> str:
        """Build API request URL."""
        return (
            f"{self.base_url}"
            f"?lat={latitude}"
            f"&lon={longitude}"
            f"&appid={self.api_key}"
            f"&units=metric"  # We convert to imperial in our code
            f"&exclude=minutely,alerts"  # We only need hourly and daily
        )

    async def _make_request(self, url: str, attempt: int) -> dict[str, Any]:
        """
        Make HTTP request to OWM API.

        Args:
            url: Request URL
            attempt: Current attempt number (0-indexed)

        Returns:
            Parsed JSON response

        Raises:
            OWMApiKeyError: Invalid API key (401)
            OWMApiRateLimitError: Rate limit exceeded (429)
            OWMApiTimeoutError: Request timeout
            OWMApiConnectionError: Connection error
            OWMApiResponseError: Invalid response
        """
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with self.session.get(url, timeout=timeout) as response:
                # Check for specific HTTP errors
                if response.status == 401:
                    _LOGGER.error("API authentication failed (401)")
                    raise OWMApiKeyError(ERROR_API_KEY_INVALID)

                if response.status == 429:
                    _LOGGER.error("API rate limit exceeded (429)")
                    raise OWMApiRateLimitError(ERROR_API_RATE_LIMIT)

                if response.status != 200:
                    error_text = await response.text()
                    _LOGGER.error(
                        "API request failed with status %d: %s",
                        response.status,
                        error_text,
                    )
                    raise OWMApiResponseError(
                        f"API returned status {response.status}: {error_text}"
                    )

                # Parse JSON response
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError as err:
                    _LOGGER.error("Invalid JSON response: %s", err)
                    raise OWMApiResponseError(
                        ERROR_API_RESPONSE
                    ) from err

                # Validate response structure
                if not self._validate_response(data):
                    _LOGGER.error("Invalid response structure")
                    raise OWMApiResponseError(
                        "Response missing required fields"
                    )

                return data

        except asyncio.TimeoutError as err:
            _LOGGER.error("Request timeout after %ds", self.timeout)
            raise OWMApiTimeoutError(ERROR_API_TIMEOUT) from err

        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error: %s", err)
            raise OWMApiConnectionError(ERROR_API_CONNECTION) from err

    def _validate_response(self, data: dict[str, Any]) -> bool:
        """
        Validate OWM API response structure.

        Args:
            data: Response data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["lat", "lon", "timezone"]

        # Check required top-level fields
        for field in required_fields:
            if field not in data:
                _LOGGER.error("Response missing required field: %s", field)
                return False

        # Check that we have either hourly or daily data
        has_hourly = "hourly" in data and isinstance(data["hourly"], list)
        has_daily = "daily" in data and isinstance(data["daily"], list)

        if not (has_hourly or has_daily):
            _LOGGER.error("Response missing forecast data")
            return False

        return True

    def _calculate_backoff(self, attempt: int) -> int:
        """
        Calculate exponential backoff delay.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        return OWM_API_RETRY_DELAY * (OWM_API_BACKOFF_FACTOR ** attempt)

    def _log_successful_call(self) -> None:
        """Log successful API call."""
        self._last_call_time = datetime.now()
        self._call_count += 1
        _LOGGER.debug(
            "API call successful (total calls: %d)", self._call_count
        )

    @property
    def call_count(self) -> int:
        """Get total number of API calls made."""
        return self._call_count

    @property
    def last_call_time(self) -> datetime | None:
        """Get timestamp of last API call."""
        return self._last_call_time

    def reset_call_count(self) -> None:
        """Reset call counter (e.g., for daily reset)."""
        _LOGGER.debug("Resetting API call counter (was %d)", self._call_count)
        self._call_count = 0
