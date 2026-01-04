# All constants and configuration
# Temperature ranges for snow ratios
# Entity names and API settings

"""Constants for the OpenWeatherMap Precipitation Forecast integration."""
from typing import Final

DOMAIN: Final = "ha_owm_precipitation_forecast"

# Configuration keys
CONF_API_KEY: Final = "api_key"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_LOCATION_NAME: Final = "location_name"
CONF_ENABLE_RAIN: Final = "enable_rain"
CONF_ENABLE_SNOW: Final = "enable_snow"
CONF_POLL_INTERVAL: Final = "poll_interval"
CONF_TEMP_RANGES: Final = "temperature_ranges"

# Default values
DEFAULT_LOCATION_NAME: Final = "Home"
DEFAULT_ENABLE_RAIN: Final = True
DEFAULT_ENABLE_SNOW: Final = True
DEFAULT_POLL_INTERVAL: Final = 60  # minutes

# Poll interval options (in minutes)
POLL_INTERVALS: Final = {
    15: "15 minutes",
    30: "30 minutes",
    60: "1 hour",
    240: "4 hours",
    480: "8 hours",
    720: "12 hours",
    1440: "24 hours",
}

# Temperature ranges for snow ratio calculation (Fahrenheit to inches of snow per inch of liquid)
DEFAULT_TEMP_RANGES: Final = {
    "above_32": {"min": 32.1, "max": 100.0, "ratio": 0.0},
    "28_to_32": {"min": 28.0, "max": 32.0, "ratio": 10.0},
    "20_to_28": {"min": 20.0, "max": 28.0, "ratio": 15.0},
    "15_to_20": {"min": 15.0, "max": 20.0, "ratio": 20.0},
    "10_to_15": {"min": 10.0, "max": 15.0, "ratio": 30.0},
    "below_10": {"min": -100.0, "max": 10.0, "ratio": 40.0},
}

# Entity name components
ENTITY_PREFIX: Final = "owm_precipitation_forecast"
ENTITY_RAIN_HOURLY: Final = "rain_hourly"
ENTITY_RAIN_DAILY: Final = "rain_daily"
ENTITY_RAIN_NEXT24H: Final = "rain_next24h"
ENTITY_SNOW_HOURLY: Final = "snow_hourly"
ENTITY_SNOW_DAILY: Final = "snow_daily"
ENTITY_SNOW_NEXT24H: Final = "snow_next24h"
ENTITY_HEALTH: Final = "health"

# Units
UNIT_INCHES: Final = "in"
UNIT_CM: Final = "cm"
UNIT_MM: Final = "mm"

# Conversions
MM_TO_INCHES: Final = 0.0393701
INCHES_TO_CM: Final = 2.54

# API
OWM_API_URL: Final = "https://api.openweathermap.org/data/3.0/onecall"
OWM_API_TIMEOUT: Final = 30

# Health status values
HEALTH_OK: Final = "ok"
HEALTH_WARNING: Final = "warning"
HEALTH_ERROR: Final = "error"
HEALTH_UNKNOWN: Final = "unknown"

# Error messages
ERROR_API_KEY_INVALID: Final = "invalid_api_key"
ERROR_LOCATION_INVALID: Final = "invalid_location"
ERROR_API_UNAVAILABLE: Final = "api_unavailable"
ERROR_RATE_LIMITED: Final = "rate_limited"
ERROR_UNKNOWN: Final = "unknown_error"

# Logging messages
LOG_SETUP_START: Final = "Setting up OpenWeatherMap Precipitation Forecast"
LOG_SETUP_COMPLETE: Final = "Setup complete for %s"
LOG_UPDATE_SUCCESS: Final = "Successfully updated precipitation data"
LOG_UPDATE_FAILED: Final = "Failed to update precipitation data: %s"
LOG_API_ERROR: Final = "API error: %s"
LOG_CALCULATION_ERROR: Final = "Calculation error: %s"
