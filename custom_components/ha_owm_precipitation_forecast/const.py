DOMAIN = "ha_owm_precipitation_forecast"
NAME_PREFIX = "owm_precipitation_forecast_"
UNIT_INCHES = "in"

CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_ENABLE_RAIN = "enable_rain"
CONF_ENABLE_SNOW = "enable_snow"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SNOW_RATIOS = "snow_ratios"

DEFAULT_ENABLE_RAIN = True
DEFAULT_ENABLE_SNOW = True
DEFAULT_SCAN_INTERVAL = 3600

DEFAULT_SNOW_RATIOS = {
    32.0: 10.0,
    20.0: 15.0,
    10.0: 20.0,
}
