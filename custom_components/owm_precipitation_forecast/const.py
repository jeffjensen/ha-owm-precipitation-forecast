"""Constants for the OWM Precipitation Forecast integration."""

from typing import Final

# Integration domain
DOMAIN: Final = "owm_precipitation_forecast"

# Integration name
NAME: Final = "OWM Precipitation Forecast"

# Version
VERSION: Final = "1.0.0"

# Configuration and options
CONF_API_KEY: Final = "api_key"
CONF_LOCATION_NAME: Final = "location_name"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_ENABLE_RAIN: Final = "enable_rain"
CONF_ENABLE_SNOW: Final = "enable_snow"
CONF_POLLING_INTERVAL: Final = "polling_interval"
CONF_SNOW_RATIOS: Final = "snow_ratios"

# Default values
DEFAULT_NAME: Final = "OWM Precipitation"
DEFAULT_ENABLE_RAIN: Final = True
DEFAULT_ENABLE_SNOW: Final = True
DEFAULT_POLLING_INTERVAL: Final = 3600  # 1 hour in seconds

# Polling interval options (in seconds)
POLLING_INTERVALS: Final = {
    "15_minutes": 900,
    "30_minutes": 1800,
    "1_hour": 3600,
    "4_hours": 14400,
    "8_hours": 28800,
    "12_hours": 43200,
    "24_hours": 86400,
}

POLLING_INTERVAL_OPTIONS: Final = [
    "15_minutes",
    "30_minutes",
    "1_hour",
    "4_hours",
    "8_hours",
    "12_hours",
    "24_hours",
]

# Temperature-adjusted snow ratios (temperature in °F: ratio)
# These represent liquid-to-snow conversion ratios based on temperature
DEFAULT_SNOW_RATIOS: Final = {
    "32": 10.0,   # 32°F and above: 10:1 ratio (wet, heavy snow)
    "28": 12.0,   # 28-31°F: 12:1 ratio
    "24": 15.0,   # 24-27°F: 15:1 ratio
    "20": 20.0,   # 20-23°F: 20:1 ratio
    "15": 25.0,   # 15-19°F: 25:1 ratio
    "10": 30.0,   # 10-14°F: 30:1 ratio
    "0": 40.0,    # 0-9°F: 40:1 ratio (light, fluffy snow)
    "-10": 50.0,  # Below 0°F: 50:1 ratio (very light, powder)
}

# Units of measurement
UNIT_INCHES: Final = "in"
UNIT_CENTIMETERS: Final = "cm"
UNIT_TEMPERATURE_FAHRENHEIT: Final = "°F"
UNIT_TEMPERATURE_CELSIUS: Final = "°C"

# Conversion factors
INCHES_TO_CM: Final = 2.54
CM_TO_INCHES: Final = 1 / 2.54

# OpenWeatherMap API
OWM_API_BASE_URL: Final = "https://api.openweathermap.org/data/3.0/onecall"
OWM_API_TIMEOUT: Final = 30
OWM_API_MAX_RETRIES: Final = 3
OWM_API_RETRY_DELAY: Final = 1  # seconds
OWM_API_BACKOFF_FACTOR: Final = 2  # exponential backoff multiplier

# Rate limiting
OWM_RATE_LIMIT_CALLS: Final = 1000  # calls per day for free tier
OWM_RATE_LIMIT_WINDOW: Final = 86400  # 24 hours in seconds
OWM_MIN_UPDATE_INTERVAL: Final = 600  # 10 minutes minimum between updates

# Entity name prefixes
ENTITY_NAME_PREFIX: Final = "owm_precipitation_forecast"

# Sensor types
SENSOR_TYPE_HOURLY_RAIN: Final = "hourly_rain"
SENSOR_TYPE_HOURLY_SNOW: Final = "hourly_snow"
SENSOR_TYPE_DAILY_RAIN: Final = "daily_rain"
SENSOR_TYPE_DAILY_SNOW: Final = "daily_snow"
SENSOR_TYPE_NEXT_24H_RAIN: Final = "next24h_rain"
SENSOR_TYPE_NEXT_24H_SNOW: Final = "next24h_snow"
SENSOR_TYPE_HEALTH: Final = "health"

# Sensor attributes
ATTR_FORECAST_TIME: Final = "forecast_time"
ATTR_ACCUMULATION: Final = "accumulation"
ATTR_HOURLY_BREAKDOWN: Final = "hourly_breakdown"
ATTR_TEMPERATURE: Final = "temperature"
ATTR_SNOW_RATIO: Final = "snow_ratio"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_NEXT_UPDATE: Final = "next_update"
ATTR_LOCATION: Final = "location"
ATTR_COORDINATES: Final = "coordinates"
ATTR_API_CALLS_TODAY: Final = "api_calls_today"
ATTR_API_CALLS_REMAINING: Final = "api_calls_remaining"
ATTR_ERROR_COUNT: Final = "error_count"
ATTR_LAST_ERROR: Final = "last_error"
ATTR_STATUS: Final = "status"

# Health status values
HEALTH_STATUS_OK: Final = "ok"
HEALTH_STATUS_WARNING: Final = "warning"
HEALTH_STATUS_ERROR: Final = "error"
HEALTH_STATUS_UNAVAILABLE: Final = "unavailable"

# Error messages
ERROR_API_KEY_INVALID: Final = "api_key_invalid"
ERROR_API_RATE_LIMIT: Final = "api_rate_limit"
ERROR_API_TIMEOUT: Final = "api_timeout"
ERROR_API_CONNECTION: Final = "api_connection"
ERROR_API_RESPONSE: Final = "api_response"
ERROR_LOCATION_INVALID: Final = "location_invalid"
ERROR_UNKNOWN: Final = "unknown"

# Coordinator update intervals
COORDINATOR_UPDATE_INTERVAL: Final = 60  # Check every minute if update needed

# Data storage keys
STORAGE_KEY: Final = f"{DOMAIN}_storage"
STORAGE_VERSION: Final = 1

# Precipitation types in OWM API response
PRECIPITATION_RAIN: Final = "rain"
PRECIPITATION_SNOW: Final = "snow"

# Time periods
HOURS_IN_DAY: Final = 24
SECONDS_IN_HOUR: Final = 3600

# Device info
MANUFACTURER: Final = "OpenWeatherMap"
MODEL: Final = "One Call API 3.0"

# Event types
EVENT_FORECAST_UPDATED: Final = f"{DOMAIN}_forecast_updated"
EVENT_API_ERROR: Final = f"{DOMAIN}_api_error"
EVENT_RATE_LIMIT_WARNING: Final = f"{DOMAIN}_rate_limit_warning"

# Service names
SERVICE_UPDATE_FORECAST: Final = "update_forecast"
SERVICE_CLEAR_ERRORS: Final = "clear_errors"

# Configuration validation
MIN_LATITUDE: Final = -90.0
MAX_LATITUDE: Final = 90.0
MIN_LONGITUDE: Final = -180.0
MAX_LONGITUDE: Final = 180.0
MIN_SNOW_RATIO: Final = 5.0
MAX_SNOW_RATIO: Final = 100.0

# Logging
LOGGER_NAME: Final = f"custom_components.{DOMAIN}"

# Icons
ICON_RAIN: Final = "mdi:weather-rainy"
ICON_SNOW: Final = "mdi:weather-snowy"
ICON_HEALTH: Final = "mdi:heart-pulse"

# Device classes
DEVICE_CLASS_PRECIPITATION: Final = "precipitation"

# State classes
STATE_CLASS_MEASUREMENT: Final = "measurement"
STATE_CLASS_TOTAL: Final = "total"

# Entity categories
ENTITY_CATEGORY_DIAGNOSTIC: Final = "diagnostic"

# Platforms
PLATFORMS: Final = ["sensor"]
