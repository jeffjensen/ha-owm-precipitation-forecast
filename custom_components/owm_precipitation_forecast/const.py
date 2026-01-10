"""Constants for OWM Precipitation Forecast integration."""

DOMAIN = "owm_precipitation_forecast"
NAME = "OWM Precipitation Forecast"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_LOCATION = "location"
CONF_SNOW_RATIO = "snow_ratio"
CONF_POLLING_INTERVAL = "polling_interval"

# Default values
DEFAULT_SNOW_RATIO = 10.0
DEFAULT_POLLING_INTERVAL = 900  # 15 minutes

# Entity types
ENTITY_SENSOR_RAIN_HOURLY = "sensor.rain_hourly_mm"
ENTITY_SENSOR_SNOW_HOURLY = "sensor.snow_hourly_cm"
ENTITY_SENSOR_ACCUMULATION_24H = "sensor.precip_accumulation_24h"
