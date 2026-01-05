from typing import Final

DOMAIN: Final = "ha_owm_precipitation_forecast"

CONF_API_KEY: Final = "api_key"
CONF_LOCATION_NAME: Final = "location_name"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_ENABLE_RAIN: Final = "enable_rain"
CONF_ENABLE_SNOW: Final = "enable_snow"
CONF_POLL_INTERVAL: Final = "poll_interval"
CONF_SNOW_RATIOS: Final = "snow_ratios"

DEFAULT_POLL_INTERVAL: Final = 3600  # 1 hour in seconds
DEFAULT_SNOW_RATIOS: Final = "-inf:15:20,15:25:15,25:inf:10"

POLL_INTERVALS: Final = {
    "15_minutes": 900,
    "30_minutes": 1800,
    "1_hour": 3600,
    "4_hours": 14400,
    "8_hours": 28800,
    "12_hours": 43200,
    "24_hours": 86400,
}

ENTITY_PREFIX: Final = "owm_precipitation_forecast_"

UNIT_INCHES: Final = "in"

OWM_API_URL: Final = "https://api.openweathermap.org/data/3.0/onecall"
