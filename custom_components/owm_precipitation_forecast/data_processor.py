"""Data processing utilities for OWM Precipitation Forecast."""

import logging
from datetime import datetime, timedelta
from typing import Any

from .models import DailyForecast, ForecastData, HourlyForecast

_LOGGER = logging.getLogger(__name__)


class PrecipitationCalculator:
    """Calculate precipitation totals from forecast data."""

    def __init__(self, forecast_data: ForecastData) -> None:
        """Initialize calculator with forecast data."""
        self.forecast_data = forecast_data

    def get_next_24h_rain(self) -> float:
        """Get total rain for next 24 hours."""
        if not self.forecast_data.hourly_forecasts:
            return 0.0

        # Take first 24 hours
        next_24h = self.forecast_data.hourly_forecasts[:24]
        total = sum(h.rain_inches for h in next_24h)

        _LOGGER.debug("Next 24h rain: %.2f inches (%d hours)", total, len(next_24h))
        return round(total, 2)

    def get_next_24h_snow(self) -> float:
        """Get total snow for next 24 hours."""
        if not self.forecast_data.hourly_forecasts:
            return 0.0

        # Take first 24 hours
        next_24h = self.forecast_data.hourly_forecasts[:24]
        total = sum(h.snow_inches for h in next_24h)

        _LOGGER.debug("Next 24h snow: %.2f inches (%d hours)", total, len(next_24h))
        return round(total, 2)

    def get_hourly_rain(self, hour_index: int = 0) -> float:
        """Get rain for a specific hour (default: next hour)."""
        if not self.forecast_data.hourly_forecasts:
            return 0.0

        if hour_index >= len(self.forecast_data.hourly_forecasts):
            return 0.0

        return self.forecast_data.hourly_forecasts[hour_index].rain_inches

    def get_hourly_snow(self, hour_index: int = 0) -> float:
        """Get snow for a specific hour (default: next hour)."""
        if not self.forecast_data.hourly_forecasts:
            return 0.0

        if hour_index >= len(self.forecast_data.hourly_forecasts):
            return 0.0

        return self.forecast_data.hourly_forecasts[hour_index].snow_inches

    def get_daily_rain(self, day_index: int = 0) -> float:
        """Get rain for a specific day (default: today)."""
        if not self.forecast_data.daily_forecasts:
            return 0.0

        if day_index >= len(self.forecast_data.daily_forecasts):
            return 0.0

        return self.forecast_data.daily_forecasts[day_index].rain_inches

    def get_daily_snow(self, day_index: int = 0) -> float:
        """Get snow for a specific day (default: today)."""
        if not self.forecast_data.daily_forecasts:
            return 0.0

        if day_index >= len(self.forecast_data.daily_forecasts):
            return 0.0

        return self.forecast_data.daily_forecasts[day_index].snow_inches

    def get_hourly_breakdown_rain(self, hours: int = 24) -> list[dict[str, Any]]:
        """
        Get hourly rain breakdown for charts/cards.

        Args:
            hours: Number of hours to include (default: 24)

        Returns:
            List of dicts with timestamp and rain amount
        """
        if not self.forecast_data.hourly_forecasts:
            return []

        breakdown = []
        for hour in self.forecast_data.hourly_forecasts[:hours]:
            breakdown.append({
                "time": hour.timestamp.isoformat(),
                "rain": hour.rain_inches,
                "probability": hour.precipitation_probability,
                "temperature": hour.temperature_f,
            })

        return breakdown

    def get_hourly_breakdown_snow(self, hours: int = 24) -> list[dict[str, Any]]:
        """
        Get hourly snow breakdown for charts/cards.

        Args:
            hours: Number of hours to include (default: 24)

        Returns:
            List of dicts with timestamp and snow amount
        """
        if not self.forecast_data.hourly_forecasts:
            return []

        breakdown = []
        for hour in self.forecast_data.hourly_forecasts[:hours]:
            breakdown.append({
                "time": hour.timestamp.isoformat(),
                "snow": hour.snow_inches,
                "probability": hour.precipitation_probability,
                "temperature": hour.temperature_f,
            })

        return breakdown

    def get_daily_breakdown_rain(self, days: int = 7) -> list[dict[str, Any]]:
        """
        Get daily rain breakdown for charts/cards.

        Args:
            days: Number of days to include (default: 7)

        Returns:
            List of dicts with date and rain amount
        """
        if not self.forecast_data.daily_forecasts:
            return []

        breakdown = []
        for day in self.forecast_data.daily_forecasts[:days]:
            breakdown.append({
                "date": day.date.date().isoformat(),
                "rain": day.rain_inches,
                "probability": day.precipitation_probability,
                "temp_high": day.temperature_high_f,
                "temp_low": day.temperature_low_f,
            })

        return breakdown

    def get_daily_breakdown_snow(self, days: int = 7) -> list[dict[str, Any]]:
        """
        Get daily snow breakdown for charts/cards.

        Args:
            days: Number of days to include (default: 7)

        Returns:
            List of dicts with date and snow amount
        """
        if not self.forecast_data.daily_forecasts:
            return []

        breakdown = []
        for day in self.forecast_data.daily_forecasts[:days]:
            breakdown.append({
                "date": day.date.date().isoformat(),
                "snow": day.snow_inches,
                "probability": day.precipitation_probability,
                "temp_high": day.temperature_high_f,
                "temp_low": day.temperature_low_f,
            })

        return breakdown

    def get_peak_precipitation_time(
        self, precipitation_type: str = "rain", hours: int = 24
    ) -> dict[str, Any] | None:
        """
        Get the hour with peak precipitation.

        Args:
            precipitation_type: "rain" or "snow"
            hours: Number of hours to check (default: 24)

        Returns:
            Dict with time, amount, and probability, or None if no precipitation
        """
        if not self.forecast_data.hourly_forecasts:
            return None

        forecasts = self.forecast_data.hourly_forecasts[:hours]
        if not forecasts:
            return None

        # Find hour with maximum precipitation
        if precipitation_type == "rain":
            peak = max(forecasts, key=lambda h: h.rain_inches)
            if peak.rain_inches == 0:
                return None
            amount = peak.rain_inches
        else:  # snow
            peak = max(forecasts, key=lambda h: h.snow_inches)
            if peak.snow_inches == 0:
                return None
            amount = peak.snow_inches

        return {
            "time": peak.timestamp.isoformat(),
            "amount": amount,
            "probability": peak.precipitation_probability,
            "temperature": peak.temperature_f,
        }

    def get_precipitation_summary(self) -> dict[str, Any]:
        """
        Get overall precipitation summary.

        Returns:
            Dict with various precipitation metrics
        """
        return {
            "next_24h_rain": self.get_next_24h_rain(),
            "next_24h_snow": self.get_next_24h_snow(),
            "next_hour_rain": self.get_hourly_rain(0),
            "next_hour_snow": self.get_hourly_snow(0),
            "today_rain": self.get_daily_rain(0),
            "today_snow": self.get_daily_snow(0),
            "peak_rain": self.get_peak_precipitation_time("rain"),
            "peak_snow": self.get_peak_precipitation_time("snow"),
            "hourly_count": len(self.forecast_data.hourly_forecasts),
            "daily_count": len(self.forecast_data.daily_forecasts),
            "last_update": self.forecast_data.last_update.isoformat(),
        }


def validate_forecast_data(data: dict[str, Any]) -> bool:
    """
    Validate forecast data structure.

    Args:
        data: Forecast data to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["lat", "lon", "timezone"]

    for field in required_fields:
        if field not in data:
            _LOGGER.error("Missing required field: %s", field)
            return False

    # Check for forecast data
    has_hourly = "hourly" in data and isinstance(data["hourly"], list)
    has_daily = "daily" in data and isinstance(data["daily"], list)

    if not (has_hourly or has_daily):
        _LOGGER.error("No forecast data found")
        return False

    return True


def extract_hourly_data(
    raw_data: dict[str, Any], max_hours: int = 48
) -> list[dict[str, Any]]:
    """
    Extract hourly forecast data.

    Args:
        raw_data: Raw OWM API response
        max_hours: Maximum number of hours to extract

    Returns:
        List of hourly forecast dicts
    """
    if "hourly" not in raw_data:
        return []

    hourly_data = raw_data["hourly"][:max_hours]
    _LOGGER.debug("Extracted %d hours of forecast data", len(hourly_data))

    return hourly_data


def extract_daily_data(
    raw_data: dict[str, Any], max_days: int = 8
) -> list[dict[str, Any]]:
    """
    Extract daily forecast data.

    Args:
        raw_data: Raw OWM API response
        max_days: Maximum number of days to extract

    Returns:
        List of daily forecast dicts
    """
    if "daily" not in raw_data:
        return []

    daily_data = raw_data["daily"][:max_days]
    _LOGGER.debug("Extracted %d days of forecast data", len(daily_data))

    return daily_data


def is_freezing_temperature(temp_f: float) -> bool:
    """
    Check if temperature is at or below freezing.

    Args:
        temp_f: Temperature in Fahrenheit

    Returns:
        True if freezing or below
    """
    return temp_f <= 32.0


def determine_precipitation_type(
    temp_f: float, has_rain: bool, has_snow: bool
) -> str:
    """
    Determine primary precipitation type.

    Args:
        temp_f: Temperature in Fahrenheit
        has_rain: Whether rain is present
        has_snow: Whether snow is present

    Returns:
        "rain", "snow", "mix", or "none"
    """
    if not has_rain and not has_snow:
        return "none"

    if has_rain and has_snow:
        return "mix"

    if is_freezing_temperature(temp_f) and has_rain:
        # Rain at freezing temps is probably freezing rain or sleet
        return "mix"

    return "snow" if has_snow else "rain"
