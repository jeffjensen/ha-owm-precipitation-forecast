"""Constants for OpenWeatherMap Precipitation Forecast integration."""

from typing import Final

# Domain
DOMAIN: Final = "owm_precipitation_forecast"
INTEGRATION_NAME: Final = "OpenWeatherMap Precipitation Forecast"

# API Configuration
OWM_API_ENDPOINT: Final = "https://api.openweathermap.org/data/3.0/onecall"
OWM_CURRENT_ENDPOINT: Final = "https://api.openweathermap.org/data/2.5/weather"
OWM_REQUEST_TIMEOUT: Final = 10  # seconds
OWM_API_ERROR_RETRY_DELAY: Final = 300  # seconds (5 minutes)

# Default Configuration
DEFAULT_POLLING_INTERVAL_MINUTES: Final = 60
DEFAULT_ENABLE_RAIN: Final = True
DEFAULT_ENABLE_SNOW: Final = True

# Temperature-Adjusted Snow Ratio Defaults (Minnesota)
# Ratios represent: 1 inch of rain = X inches of snow at that temperature
DEFAULT_COLD_TEMP_THRESHOLD_F: Final = 25  # Below 25F
DEFAULT_COLD_TEMP_RATIO: Final = 15.0  # 15:1 ratio for very cold snow

DEFAULT_WARM_TEMP_THRESHOLD_F: Final = 32  # Above 32F
DEFAULT_WARM_TEMP_RATIO: Final = 5.0  # 5:1 ratio for wet snow

DEFAULT_TRANSITIONAL_TEMP_RATIO: Final = 10.0  # 10:1 ratio (25-32F)

# Polling Intervals (minutes)
POLLING_INTERVALS: Final = [15, 30, 60, 240, 480, 720, 1440]
POLLING_INTERVAL_NAMES: Final = {
    15: "15 minutes",
    30: "30 minutes",
    60: "1 hour",
    240: "4 hours",
    480: "8 hours",
    720: "12 hours",
    1440: "24 hours",
}

# Unit of Measurement
UNIT_INCHES: Final = "in"
UNIT_MILLIMETERS: Final = "mm"
UNIT_CELSIUS: Final = "C"
UNIT_FAHRENHEIT: Final = "F"

# Conversion Factors
MM_TO_INCHES: Final = 0.0393701  # 1 mm = 0.0393701 inches
INCHES_TO_MM: Final = 25.4  # 1 inch = 25.4 mm

# Entity Naming
ENTITY_PREFIX: Final = "owm_precipitation_forecast"
ENTITY_RAIN_HOURLY: Final = f"{ENTITY_PREFIX}_rain_hourly"
ENTITY_RAIN_DAILY: Final = f"{ENTITY_PREFIX}_rain_daily"
ENTITY_RAIN_NEXT24H: Final = f"{ENTITY_PREFIX}_rain_next24h"
ENTITY_SNOW_HOURLY: Final = f"{ENTITY_PREFIX}_snow_hourly"
ENTITY_SNOW_DAILY: Final = f"{ENTITY_PREFIX}_snow_daily"
ENTITY_SNOW_NEXT24H: Final = f"{ENTITY_PREFIX}_snow_next24h"
ENTITY_HEALTH: Final = f"{ENTITY_PREFIX}_health"

# Attributes
ATTR_FORECAST: Final = "forecast"
ATTR_TIMESTAMP: Final = "timestamp"
ATTR_LOCATION: Final = "location"
ATTR_LATITUDE: Final = "latitude"
ATTR_LONGITUDE: Final = "longitude"
ATTR_LAST_UPDATE: Final = "last_update"
ATTR_LAST_ERROR: Final = "last_error"
ATTR_NEXT_UPDATE: Final = "next_update"
ATTR_API_CALLS: Final = "api_calls_today"
ATTR_HOURLY_BREAKDOWN: Final = "hourly_breakdown"

# Config Entry Keys
CONF_API_KEY: Final = "api_key"
CONF_LOCATION_NAME: Final = "location_name"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_ENABLE_RAIN: Final = "enable_rain"
CONF_ENABLE_SNOW: Final = "enable_snow"
CONF_POLLING_INTERVAL: Final = "polling_interval_minutes"
CONF_COLD_TEMP_THRESHOLD: Final = "cold_temp_threshold"
CONF_COLD_TEMP_RATIO: Final = "cold_temp_ratio"
CONF_WARM_TEMP_THRESHOLD: Final = "warm_temp_threshold"
CONF_WARM_TEMP_RATIO: Final = "warm_temp_ratio"

# Service Names
SERVICE_FORCE_UPDATE: Final = "force_update"
SERVICE_RELOAD_RATIOS: Final = "reload_snow_ratios"

# Error Messages
ERROR_INVALID_API_KEY: Final = "invalid_api_key"
ERROR_CANNOT_CONNECT: Final = "cannot_connect"
ERROR_INVALID_LOCATION: Final = "invalid_location"
ERROR_ALREADY_CONFIGURED: Final = "already_configured"
ERROR_API_TIMEOUT: Final = "API request timeout"
ERROR_API_ERROR: Final = "API returned error"
ERROR_INVALID_RESPONSE: Final = "Invalid response format from API"

# Logging
LOG_INTEGRATION_SETUP: Final = "Setting up OpenWeatherMap Precipitation Forecast"
LOG_INTEGRATION_UNLOAD: Final = "Unloading OpenWeatherMap Precipitation Forecast"
LOG_CONFIG_FLOW_INIT: Final = "Config flow initiated by user"
LOG_OPTIONS_FLOW_INIT: Final = "Options flow initiated by user"
LOG_API_CALL: Final = "Calling OpenWeatherMap API"
LOG_API_SUCCESS: Final = "Successfully retrieved forecast data"
LOG_API_ERROR: Final = "Error calling OpenWeatherMap API"
LOG_ENTITY_UPDATE: Final = "Updating sensor entity"
LOG_ENTITY_CREATE: Final = "Creating sensor entity"

# Data Model
DATA_COORDINATOR: Final = "coordinator"
DATA_ENTITIES: Final = "entities"

# Health Status
HEALTH_HEALTHY: Final = "Healthy"
HEALTH_UNHEALTHY: Final = "Unhealthy"
HEALTH_UNKNOWN: Final = "Unknown"
