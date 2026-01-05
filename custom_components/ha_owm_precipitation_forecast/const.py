"""Constants for the OpenWeatherMap Precipitation Forecast integration."""
from typing import Final

# Domain
DOMAIN: Final = "ha_owm_precipitation_forecast"
LOGGER_NAME: Final = f"custom_components.{DOMAIN}"

# Configuration keys
CONF_LOCATION_NAME: Final = "location_name"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_API_KEY: Final = "api_key"
CONF_ENABLE_RAIN: Final = "enable_rain"
CONF_ENABLE_SNOW: Final = "enable_snow"
CONF_UPDATE_INTERVAL: Final = "update_interval"
CONF_SNOW_RATIOS: Final = "snow_ratios"

# Defaults
DEFAULT_LOCATION_NAME: Final = "home"
DEFAULT_ENABLE_RAIN: Final = True
DEFAULT_ENABLE_SNOW: Final = True
DEFAULT_UPDATE_INTERVAL: Final = 60  # minutes

# Update intervals (in minutes)
UPDATE_INTERVALS: Final = {
    "15min": 15,
    "30min": 30,
    "1h": 60,
    "4h": 240,
    "8h": 480,
    "12h": 720,
    "24h": 1440,
}

# Default temperature-adjusted snow ratios (temp_f: ratio)
DEFAULT_SNOW_RATIOS: Final = {
    "below_15": 20.0,
    "15_to_20": 18.0,
    "20_to_25": 15.0,
    "25_to_30": 12.0,
    "30_to_32": 10.0,
    "above_32": 0.0,
}

# Entity naming
ENTITY_PREFIX: Final = "owm_precipitation_forecast"
ENTITY_RAIN_HOURLY: Final = "rain_hourly"
ENTITY_RAIN_DAILY: Final = "rain_daily"
ENTITY_RAIN_NEXT24H: Final = "rain_next24h"
ENTITY_SNOW_HOURLY: Final = "snow_hourly"
ENTITY_SNOW_DAILY: Final = "snow_daily"
ENTITY_SNOW_NEXT24H: Final = "snow_next24h"
ENTITY_HEALTH: Final = "health"

# Unit of measurement
UNIT_INCHES: Final = "in"
UNIT_CENTIMETERS: Final = "cm"

# Attributes
ATTR_FORECAST_DATA: Final = "forecast_data"
ATTR_LOCATION: Final = "location"
ATTR_TIMESTAMP: Final = "timestamp"
ATTR_ACCUMULATION: Final = "accumulation"
ATTR_TEMPERATURE: Final = "temperature"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_API_STATUS: Final = "api_status"
ATTR_ERROR_COUNT: Final = "error_count"
ATTR_LAST_ERROR: Final = "last_error"

# OpenWeatherMap API
OWM_API_ENDPOINT: Final = "https://api.openweathermap.org/data/3.0/onecall"
OWM_API_TIMEOUT: Final = 30

# Error messages
ERROR_API_KEY_INVALID: Final = "Invalid API key"
ERROR_API_RATE_LIMIT: Final = "API rate limit exceeded"
ERROR_API_COMMUNICATION: Final = "Error communicating with OpenWeatherMap API"
ERROR_INVALID_COORDINATES: Final = "Invalid coordinates"
ERROR_UNKNOWN: Final = "Unknown error occurred"

# Status messages
STATUS_OK: Final = "OK"
STATUS_ERROR: Final = "Error"
STATUS_WARNING: Final = "Warning"
