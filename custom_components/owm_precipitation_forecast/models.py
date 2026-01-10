"""Data models for OWM Precipitation Forecast."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class HourlyForecast:
    """Hourly precipitation forecast data."""

    timestamp: datetime
    temperature_f: float
    rain_inches: float
    snow_inches: float
    precipitation_probability: float

    @classmethod
    def from_owm_data(
        cls, data: dict[str, Any], snow_ratios: dict[str, float]
    ) -> "HourlyForecast":
        """Create HourlyForecast from OWM API data."""
        from .helpers import (
            calculate_snow_from_liquid,
            celsius_to_fahrenheit,
        )

        # Extract timestamp
        timestamp = datetime.fromtimestamp(data["dt"])

        # Extract temperature (convert from Celsius to Fahrenheit)
        temp_c = data.get("temp", 0)
        temperature_f = celsius_to_fahrenheit(temp_c)

        # Extract rain (in mm, convert to inches)
        rain_mm = data.get("rain", {}).get("1h", 0)
        rain_inches = rain_mm / 25.4  # mm to inches

        # Calculate snow based on temperature and liquid precipitation
        # OWM provides snow in mm, but we want temperature-adjusted calculation
        snow_mm = data.get("snow", {}).get("1h", 0)
        if snow_mm > 0:
            # Use OWM's snow value as liquid equivalent if provided
            snow_liquid_inches = snow_mm / 25.4
            snow_inches = calculate_snow_from_liquid(
                snow_liquid_inches, temperature_f, snow_ratios
            )
        elif temperature_f <= 32 and rain_mm > 0:
            # Convert rain to snow if temperature is freezing
            snow_inches = calculate_snow_from_liquid(
                rain_inches, temperature_f, snow_ratios
            )
            rain_inches = 0  # It's snow, not rain
        else:
            snow_inches = 0

        # Extract precipitation probability
        precipitation_probability = data.get("pop", 0) * 100  # Convert to percentage

        return cls(
            timestamp=timestamp,
            temperature_f=temperature_f,
            rain_inches=round(rain_inches, 2),
            snow_inches=round(snow_inches, 2),
            precipitation_probability=round(precipitation_probability, 1),
        )


@dataclass
class DailyForecast:
    """Daily precipitation forecast data."""

    date: datetime
    temperature_high_f: float
    temperature_low_f: float
    rain_inches: float
    snow_inches: float
    precipitation_probability: float

    @classmethod
    def from_owm_data(
        cls, data: dict[str, Any], snow_ratios: dict[str, float]
    ) -> "DailyForecast":
        """Create DailyForecast from OWM API data."""
        from .helpers import (
            calculate_snow_from_liquid,
            celsius_to_fahrenheit,
        )

        # Extract date
        date = datetime.fromtimestamp(data["dt"])

        # Extract temperatures
        temp_data = data.get("temp", {})
        temp_high_c = temp_data.get("max", 0)
        temp_low_c = temp_data.get("min", 0)
        temperature_high_f = celsius_to_fahrenheit(temp_high_c)
        temperature_low_f = celsius_to_fahrenheit(temp_low_c)

        # Use average temperature for snow calculation
        avg_temp_f = (temperature_high_f + temperature_low_f) / 2

        # Extract rain
        rain_mm = data.get("rain", 0)
        rain_inches = rain_mm / 25.4

        # Calculate snow
        snow_mm = data.get("snow", 0)
        if snow_mm > 0:
            snow_liquid_inches = snow_mm / 25.4
            snow_inches = calculate_snow_from_liquid(
                snow_liquid_inches, avg_temp_f, snow_ratios
            )
        elif avg_temp_f <= 32 and rain_mm > 0:
            snow_inches = calculate_snow_from_liquid(
                rain_inches, avg_temp_f, snow_ratios
            )
            rain_inches = 0
        else:
            snow_inches = 0

        # Extract precipitation probability
        precipitation_probability = data.get("pop", 0) * 100

        return cls(
            date=date,
            temperature_high_f=round(temperature_high_f, 1),
            temperature_low_f=round(temperature_low_f, 1),
            rain_inches=round(rain_inches, 2),
            snow_inches=round(snow_inches, 2),
            precipitation_probability=round(precipitation_probability, 1),
        )


@dataclass
class ForecastData:
    """Complete forecast data."""

    location_name: str
    latitude: float
    longitude: float
    hourly_forecasts: list[HourlyForecast]
    daily_forecasts: list[DailyForecast]
    last_update: datetime
    timezone: str

    def get_hourly_rain_total(self, hours: int = 24) -> float:
        """Get total rain for next N hours."""
        return sum(
            h.rain_inches for h in self.hourly_forecasts[:hours]
        )

    def get_hourly_snow_total(self, hours: int = 24) -> float:
        """Get total snow for next N hours."""
        return sum(
            h.snow_inches for h in self.hourly_forecasts[:hours]
        )

    def get_daily_rain_total(self, days: int = 7) -> float:
        """Get total rain for next N days."""
        return sum(
            d.rain_inches for d in self.daily_forecasts[:days]
        )

    def get_daily_snow_total(self, days: int = 7) -> float:
        """Get total snow for next N days."""
        return sum(
            d.snow_inches for d in self.daily_forecasts[:days]
        )


@dataclass
class ApiCallStats:
    """API call statistics for rate limiting."""

    total_calls_today: int
    last_call_time: datetime
    error_count: int
    last_error: str | None
    last_error_time: datetime | None

    def increment_calls(self) -> None:
        """Increment call counter."""
        self.total_calls_today += 1
        self.last_call_time = datetime.now()

    def increment_errors(self, error: str) -> None:
        """Increment error counter."""
        self.error_count += 1
        self.last_error = error
        self.last_error_time = datetime.now()

    def reset_daily_stats(self) -> None:
        """Reset daily statistics."""
        self.total_calls_today = 0

    def should_throttle(self, max_calls: int) -> bool:
        """Check if we should throttle API calls."""
        return self.total_calls_today >= max_calls


@dataclass
class HealthStatus:
    """Integration health status."""

    status: str  # ok, warning, error, unavailable
    api_calls_today: int
    api_calls_remaining: int
    error_count: int
    last_error: str | None
    last_update: datetime | None
    next_update: datetime | None

    @property
    def is_healthy(self) -> bool:
        """Check if integration is healthy."""
        return self.status == "ok"

    @property
    def has_errors(self) -> bool:
        """Check if there are errors."""
        return self.error_count > 0
