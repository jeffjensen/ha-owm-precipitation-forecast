"""Data update coordinator for OWM Precipitation Forecast."""

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import OWMApiClient
from .const import (
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    CONF_POLLING_INTERVAL,
    CONF_SNOW_RATIOS,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_SNOW_RATIOS,
    DOMAIN,
    EVENT_API_ERROR,
    EVENT_FORECAST_UPDATED,
    EVENT_RATE_LIMIT_WARNING,
    HEALTH_STATUS_ERROR,
    HEALTH_STATUS_OK,
    HEALTH_STATUS_UNAVAILABLE,
    HEALTH_STATUS_WARNING,
    OWM_RATE_LIMIT_CALLS,
)
from .exceptions import OWMApiError, OWMApiKeyError, OWMApiRateLimitError
from .models import (
    ApiCallStats,
    DailyForecast,
    ForecastData,
    HealthStatus,
    HourlyForecast,
)

_LOGGER = logging.getLogger(__name__)


class OWMPrecipitationCoordinator(DataUpdateCoordinator[ForecastData]):
    """Class to manage fetching OWM precipitation data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.location_name = entry.data[CONF_LOCATION_NAME]
        self.latitude = entry.data[CONF_LATITUDE]
        self.longitude = entry.data[CONF_LONGITUDE]

        # Get configuration from options
        self.snow_ratios = entry.options.get(CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS)
        polling_interval = entry.options.get(
            CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
        )

        # Initialize API client
        self.api_client = OWMApiClient(entry.data[CONF_API_KEY], hass)

        # Initialize API call statistics
        self.api_stats = ApiCallStats(
            total_calls_today=0,
            last_call_time=datetime.now(),
            error_count=0,
            last_error=None,
            last_error_time=None,
        )

        # Initialize health status
        self._health_status = HealthStatus(
            status=HEALTH_STATUS_OK,
            api_calls_today=0,
            api_calls_remaining=OWM_RATE_LIMIT_CALLS,
            error_count=0,
            last_error=None,
            last_update=None,
            next_update=None,
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.location_name}",
            update_interval=timedelta(seconds=polling_interval),
        )

    async def _async_update_data(self) -> ForecastData:
        """Fetch data from API endpoint.

        Returns:
            ForecastData object with current forecast

        Raises:
            UpdateFailed: If update fails
        """
        try:
            # Check rate limiting
            if self._should_throttle():
                _LOGGER.warning(
                    "Rate limit approaching, throttling requests for %s",
                    self.location_name,
                )
                self._update_health_status(HEALTH_STATUS_WARNING, "Rate limit warning")
                self._fire_event(EVENT_RATE_LIMIT_WARNING)
                raise UpdateFailed("Rate limit warning - throttling requests")

            # Fetch data from OWM API
            _LOGGER.debug("Fetching forecast data for %s", self.location_name)
            raw_data = await self.api_client.get_forecast(
                self.latitude, self.longitude
            )

            # Update API statistics
            self.api_stats.increment_calls()
            self._update_api_calls_tracking()

            # Process and transform data
            forecast_data = self._process_forecast_data(raw_data)

            # Update health status
            self._update_health_status(HEALTH_STATUS_OK)
            self._fire_event(EVENT_FORECAST_UPDATED, {"location": self.location_name})

            _LOGGER.info(
                "Successfully updated forecast for %s (hourly: %d, daily: %d)",
                self.location_name,
                len(forecast_data.hourly_forecasts),
                len(forecast_data.daily_forecasts),
            )

            return forecast_data

        except OWMApiKeyError as err:
            error_msg = f"API key invalid: {err}"
            _LOGGER.error(error_msg)
            self.api_stats.increment_errors(str(err))
            self._update_health_status(HEALTH_STATUS_ERROR, error_msg)
            self._fire_event(EVENT_API_ERROR, {"error": error_msg})
            raise UpdateFailed(error_msg) from err

        except OWMApiRateLimitError as err:
            error_msg = f"Rate limit exceeded: {err}"
            _LOGGER.error(error_msg)
            self.api_stats.increment_errors(str(err))
            self._update_health_status(HEALTH_STATUS_ERROR, error_msg)
            self._fire_event(EVENT_API_ERROR, {"error": error_msg})
            raise UpdateFailed(error_msg) from err

        except OWMApiError as err:
            error_msg = f"API error: {err}"
            _LOGGER.error(error_msg)
            self.api_stats.increment_errors(str(err))
            self._update_health_status(HEALTH_STATUS_ERROR, error_msg)
            self._fire_event(EVENT_API_ERROR, {"error": error_msg})
            raise UpdateFailed(error_msg) from err

        except Exception as err:
            error_msg = f"Unexpected error: {err}"
            _LOGGER.exception("Unexpected error updating forecast for %s", self.location_name)
            self.api_stats.increment_errors(str(err))
            self._update_health_status(HEALTH_STATUS_ERROR, error_msg)
            self._fire_event(EVENT_API_ERROR, {"error": error_msg})
            raise UpdateFailed(error_msg) from err

    def _process_forecast_data(self, raw_data: dict[str, Any]) -> ForecastData:
        """
        Process raw OWM API data into ForecastData model.

        Args:
            raw_data: Raw data from OWM API

        Returns:
            ForecastData object
        """
        # Process hourly forecasts
        hourly_forecasts: list[HourlyForecast] = []
        if "hourly" in raw_data:
            for hour_data in raw_data["hourly"]:
                try:
                    forecast = HourlyForecast.from_owm_data(
                        hour_data, self.snow_ratios
                    )
                    hourly_forecasts.append(forecast)
                except Exception as err:
                    _LOGGER.warning("Failed to process hourly data: %s", err)
                    continue

        # Process daily forecasts
        daily_forecasts: list[DailyForecast] = []
        if "daily" in raw_data:
            for day_data in raw_data["daily"]:
                try:
                    forecast = DailyForecast.from_owm_data(
                        day_data, self.snow_ratios
                    )
                    daily_forecasts.append(forecast)
                except Exception as err:
                    _LOGGER.warning("Failed to process daily data: %s", err)
                    continue

        _LOGGER.debug(
            "Processed %d hourly and %d daily forecasts",
            len(hourly_forecasts),
            len(daily_forecasts),
        )

        return ForecastData(
            location_name=self.location_name,
            latitude=raw_data["lat"],
            longitude=raw_data["lon"],
            hourly_forecasts=hourly_forecasts,
            daily_forecasts=daily_forecasts,
            last_update=datetime.now(),
            timezone=raw_data.get("timezone", "UTC"),
        )

    def _should_throttle(self) -> bool:
        """
        Check if we should throttle API calls.

        Returns:
            True if should throttle
        """
        # Warn at 80% of rate limit
        warning_threshold = int(OWM_RATE_LIMIT_CALLS * 0.8)
        return self.api_stats.total_calls_today >= warning_threshold

    def _update_api_calls_tracking(self) -> None:
        """Update API call tracking."""
        # Reset counter daily
        now = datetime.now()
        if self.api_stats.last_call_time:
            time_diff = now - self.api_stats.last_call_time
            if time_diff.days >= 1:
                _LOGGER.debug("Resetting daily API call counter")
                self.api_stats.reset_daily_stats()

    def _update_health_status(
        self, status: str, error: str | None = None
    ) -> None:
        """
        Update integration health status.

        Args:
            status: Health status (ok, warning, error, unavailable)
            error: Optional error message
        """
        self._health_status.status = status
        self._health_status.api_calls_today = self.api_stats.total_calls_today
        self._health_status.api_calls_remaining = max(
            0, OWM_RATE_LIMIT_CALLS - self.api_stats.total_calls_today
        )
        self._health_status.error_count = self.api_stats.error_count

        if error:
            self._health_status.last_error = error

        if status in (HEALTH_STATUS_OK, HEALTH_STATUS_WARNING):
            self._health_status.last_update = datetime.now()
            if self.update_interval:
                self._health_status.next_update = datetime.now() + self.update_interval

        _LOGGER.debug(
            "Health status updated: %s (API calls: %d, errors: %d)",
            status,
            self.api_stats.total_calls_today,
            self.api_stats.error_count,
        )

    def _fire_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """
        Fire a Home Assistant event.

        Args:
            event_type: Event type
            data: Optional event data
        """
        event_data = {
            "location": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }
        if data:
            event_data.update(data)

        self.hass.bus.async_fire(event_type, event_data)

    @property
    def health_status(self) -> HealthStatus:
        """Get current health status."""
        return self._health_status

    def clear_errors(self) -> None:
        """Clear error counters and reset health status."""
        _LOGGER.info("Clearing errors for %s", self.location_name)
        self.api_stats.error_count = 0
        self.api_stats.last_error = None
        self.api_stats.last_error_time = None
        self._update_health_status(HEALTH_STATUS_OK)

    async def async_update_options(self) -> None:
        """Update coordinator when options change."""
        _LOGGER.debug("Updating coordinator options for %s", self.location_name)

        # Update snow ratios
        self.snow_ratios = self.entry.options.get(
            CONF_SNOW_RATIOS, DEFAULT_SNOW_RATIOS
        )

        # Update polling interval
        polling_interval = self.entry.options.get(
            CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL
        )
        self.update_interval = timedelta(seconds=polling_interval)

        # Request refresh with new settings
        await self.async_request_refresh()
