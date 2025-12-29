from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "owm_precipitation_forecast"

CONF_API_KEY: Final = "api_key"
CONF_LOCATION_NAME: Final = "location_name"
CONF_LOCATION_SLUG: Final = "location_slug"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_POLLING_INTERVAL: Final = "polling_interval"
CONF_ENABLE_RAIN: Final = "enable_rain"
CONF_ENABLE_SNOW: Final = "enable_snow"
CONF_UNIT_SYSTEM: Final = "unit_system"
CONF_SNOW_RATIO_MODE: Final = "snow_ratio_mode"
CONF_SNOW_RATIO_CONFIG: Final = "snow_ratio_config"

DEFAULT_ENABLE_RAIN: Final = True
DEFAULT_ENABLE_SNOW: Final = True
DEFAULT_UNIT_SYSTEM: Final = "in"  # exposure; internal always inches
DEFAULT_POLLING_INTERVAL: Final = 60  # minutes
DEFAULT_SNOW_RATIO_MODE: Final = "preset"

POLLING_INTERVAL_OPTIONS: Final[dict[int, timedelta]] = {
    15: timedelta(minutes=15),
    30: timedelta(minutes=30),
    60: timedelta(hours=1),
    240: timedelta(hours=4),
    480: timedelta(hours=8),
    720: timedelta(hours=12),
    1440: timedelta(hours=24),
}

# OWM
OWM_ONECALL_URL: Final = "https://api.openweathermap.org/data/3.0/onecall"
OWM_UNITS: Final = "metric"  # we get mm, °C, convert internally

# Entity / attribute keys
ATTR_RAIN_IN: Final = "rain_inches"
ATTR_SNOW_IN: Final = "snow_inches"
ATTR_TEMP_F: Final = "temperature_f"
ATTR_TEMP_RANGE_F: Final = "temperature_range_f"
ATTR_SNOW_RATIO_USED: Final = "snow_ratio_used"
ATTR_SNOW_RATIO_PROFILE: Final = "snow_ratio_profile"
ATTR_FORECAST_TIMESTAMP: Final = "forecast_timestamp"
ATTR_FORECAST_DATE: Final = "forecast_date"
ATTR_FORECAST_HOURS: Final = "forecast_hours"

# Health attributes
ATTR_LAST_SUCCESSFUL_UPDATE: Final = "last_successful_update"
ATTR_LAST_API_ERROR: Final = "last_api_error"
ATTR_CONSECUTIVE_FAILURES: Final = "consecutive_failures"
ATTR_API_STATUS: Final = "api_status"
ATTR_POLLING_INTERVAL_MINUTES: Final = "polling_interval"
ATTR_LOCATION_NAME: Final = "location_name"

API_STATUS_OK: Final = "ok"
API_STATUS_DEGRADED: Final = "degraded"
API_STATUS_FAILED: Final = "failed"

PLATFORM_SENSOR: Final = "sensor"
PLATFORM_BINARY_SENSOR: Final = "binary_sensor"

HEALTH_ENTITY_SUFFIX: Final = "health"

# Snow ratio presets (temperature in F)
DEFAULT_SNOW_RATIO_CONFIG: Final[dict[str, float]] = {
    "below_0f": 20.0,
    "0_to_15f": 15.0,
    "15_to_32f": 10.0,
    "above_32f": 0.0,
}

SNOW_RATIO_PRESET_DRY: Final[dict[str, float]] = {
    "below_0f": 22.0,
    "0_to_15f": 18.0,
    "15_to_32f": 12.0,
    "above_32f": 0.0,
}

SNOW_RATIO_PRESET_WET: Final[dict[str, float]] = {
    "below_0f": 18.0,
    "0_to_15f": 14.0,
    "15_to_32f": 8.0,
    "above_32f": 0.0,
}

SNOW_RATIO_PRESETS: Final[dict[str, dict[str, float]]] = {
    "default": DEFAULT_SNOW_RATIO_CONFIG,
    "dry": SNOW_RATIO_PRESET_DRY,
    "wet": SNOW_RATIO_PRESET_WET,
}
