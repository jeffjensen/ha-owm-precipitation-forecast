"""Constants for OpenWeatherMap Precipitation Forecast integration."""
from __future__ import annotations

import logging
from typing import Final

LOGGER: logging.Logger = logging.getLogger(__name__)

DOMAIN: Final = "ha_owm_precipitation_forecast"
NAME: Final = "OpenWeatherMap Precipitation Forecast"
VERSION: Final = "1.0.0"

PLATFORMS: Final = ["sensor"]

# Config flow keys
CONF_API_KEY: Final = "api_key"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_LOCATION_NAME: Final = "location_name"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_ENABLE_RAIN: Final = "enable_rain"
CONF_ENABLE_SNOW: Final = "enable_snow"
CONF_SNOW_RATIO: Final = "snow_ratio"
CONF_RAIN_ENABLED: Final = "rain_enabled"
CONF_SNOW_ENABLED: Final = "snow_enabled"
CONF_TEMPERATURE_ADJUSTED_RATIO: Final = "temperature_adjusted_ratio"

# Scan interval options (minutes)
SCAN_INTERVALS: Final = {
    "15": 15,
    "30": 30,
    "60": 60,
    "240": 240,
    "480": 480,
    "720": 720,
    "1440": 1440,
}
DEFAULT_SCAN_INTERVAL: Final = 60

# Snow ratio defaults
DEFAULT_SNOW_RATIO: Final = 10.0
MIN_SNOW_RATIO: Final = 1.0
MAX_SNOW_RATIO: Final = 50.0

# Unit conversions
MM_TO_INCHES: Final = 0.0393701
INCHES_TO_CM: Final = 2.54

# Entity naming
ENTITY_PREFIX: Final = "owm_precipitation_forecast"

# Sensor types
SENSOR_HOURLY_RAIN: Final = "hourly_rain"
SENSOR_HOURLY_SNOW: Final = "hourly_snow"
SENSOR_DAILY_RAIN: Final = "daily_rain"
SENSOR_DAILY_SNOW: Final = "daily_snow"
SENSOR_NEXT24H_RAIN: Final = "next24h_rain"
SENSOR_NEXT24H_SNOW: Final = "next24h_snow"
SENSOR_HEALTH: Final = "health"

SENSOR_TYPES: Final = [
    SENSOR_HOURLY_RAIN,
    SENSOR_HOURLY_SNOW,
    SENSOR_DAILY_RAIN,
    SENSOR_DAILY_SNOW,
    SENSOR_NEXT24H_RAIN,
    SENSOR_NEXT24H_SNOW,
    SENSOR_HEALTH,
]

# Unit of measurement
UOM_INCHES: Final = "in"
UOM_CENTIMETERS: Final = "cm"

# Temperature ranges for snow ratio (Fahrenheit)
SNOW_RATIO_RANGES: Final = {
    (-float('inf'), 0): 20.0,      # Very cold
    (0, 10): 18.0,                 # Optimal fluffy
    (10, 20): 14.0,               # Cold
    (20, 28): 12.0,               # Cool
    (28, 32): 8.0,                # Near freezing
    (32, float('inf')): 0.0,      # Warm (rain)
}

# API rate limiting
API_TIMEOUT: Final = 10
MAX_RETRIES: Final = 3
RETRY_DELAY: Final = 5

# Health status values
HEALTH_STATUS_OK: Final = "ok"
HEALTH_STATUS_ERROR: Final = "error"
HEALTH_STATUS_UNAVAILABLE: Final = "unavailable"

# Error messages
ERROR_API_KEY: Final = "Invalid API key"
ERROR_LOCATION: Final = "Invalid location coordinates"
ERROR_API_TIMEOUT: Final = "API request timeout"
ERROR_UNKNOWN: Final = "Unknown error occurred"
