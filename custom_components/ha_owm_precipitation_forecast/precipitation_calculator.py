# Processes raw API data into usable precipitation totals
# Applies temperature-adjusted snow ratios
# Calculates hourly, daily, and 24-hour forecasts
# Converts units (mm to inches)

"""Precipitation calculation logic."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from .const import DEFAULT_TEMP_RANGES, MM_TO_INCHES

_LOGGER = logging.getLogger(__name__)


class PrecipitationCalculator:
    """Calculate precipitation totals with temperature-adjusted snow ratios."""

    def __init__(self, temp_ranges: dict[str, dict[str, float]] | None = None) -> None:
        """Initialize the calculator."""
        self._temp_ranges = temp_ranges or DEFAULT_TEMP_RANGES
        _LOGGER.debug("Initialized calculator with temperature ranges")

    def calculate_snow_from_rain(
        self, rain_inches: float, temperature_f: float
    ) -> float:
        """Convert liquid precipitation to snow using temperature-based ratio.

        Args:
            rain_inches: Liquid precipitation in inches
            temperature_f: Temperature in Fahrenheit

        Returns:
            Snow accumulation in inches
        """
        if rain_inches == 0:
            return 0.0

        # Find the appropriate ratio for the temperature
        ratio = 0.0
        for range_data in self._temp_ranges.values():
            if range_data["min"] <= temperature_f <= range_data["max"]:
                ratio = range_data["ratio"]
                break

        snow_inches = rain_inches * ratio
        _LOGGER.debug(
            "Converted %.3f in rain at %.1f°F to %.3f in snow (ratio: %.1f:1)",
            rain_inches,
            temperature_f,
            snow_inches,
            ratio,
        )
        return snow_inches

    def process_forecast_data(
        self, forecast_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process raw forecast data into precipitation totals.

        Args:
            forecast_data: Raw data from OpenWeatherMap API

        Returns:
            Processed precipitation data with hourly, daily, and 24h totals
        """
        hourly_data = forecast_data.get("hourly", [])
        daily_data = forecast_data.get("daily", [])

        result = {
            "hourly_rain": [],
            "hourly_snow": [],
            "daily_rain": [],
            "daily_snow": [],
            "next24h_rain": 0.0,
            "next24h_snow": 0.0,
            "last_update": datetime.now(),
        }

        # Process hourly data
        now = datetime.now()
        next_24h_cutoff = now + timedelta(hours=24)

        for hour in hourly_data[:48]:  # Process up to 48 hours
            timestamp = datetime.fromtimestamp(hour.get("dt", 0))
            temp_f = hour.get("temp", 32.0)

            # Get rain (in mm, convert to inches)
            rain_mm = hour.get("rain", {}).get("1h", 0) if isinstance(hour.get("rain"), dict) else 0
            rain_inches = rain_mm * MM_TO_INCHES

            # Calculate snow
            snow_inches = self.calculate_snow_from_rain(rain_inches, temp_f)

            hourly_entry = {
                "timestamp": timestamp,
                "rain_inches": round(rain_inches, 3),
                "snow_inches": round(snow_inches, 3),
                "temperature_f": temp_f,
            }

            result["hourly_rain"].append(hourly_entry)
            result["hourly_snow"].append(hourly_entry)

            # Accumulate next 24h totals
            if timestamp <= next_24h_cutoff:
                result["next24h_rain"] += rain_inches
                result["next24h_snow"] += snow_inches

        # Process daily data
        for day in daily_data[:8]:  # Process up to 8 days
            timestamp = datetime.fromtimestamp(day.get("dt", 0))
            temp_f = day.get("temp", {}).get("day", 32.0)

            # Get rain (in mm, convert to inches)
            rain_mm = day.get("rain", 0)
            rain_inches = rain_mm * MM_TO_INCHES

            # Calculate snow
            snow_inches = self.calculate_snow_from_rain(rain_inches, temp_f)

            daily_entry = {
                "timestamp": timestamp,
                "rain_inches": round(rain_inches, 3),
                "snow_inches": round(snow_inches, 3),
                "temperature_f": temp_f,
            }

            result["daily_rain"].append(daily_entry)
            result["daily_snow"].append(daily_entry)

        # Round next 24h totals
        result["next24h_rain"] = round(result["next24h_rain"], 3)
        result["next24h_snow"] = round(result["next24h_snow"], 3)

        _LOGGER.debug(
            "Processed forecast: %d hourly, %d daily entries. Next 24h: %.3f in rain, %.3f in snow",
            len(result["hourly_rain"]),
            len(result["daily_rain"]),
            result["next24h_rain"],
            result["next24h_snow"],
        )

        return result
