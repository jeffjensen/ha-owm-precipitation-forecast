from datetime import timedelta

DOMAIN = "owm_precipitation_forecast"
CONF_API_KEY = "api_key"
CONF_LOCATION_NAME = "location_name"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_POLLING_INTERVAL = "polling_interval"

# Feature Toggles
CONF_ENABLE_SNOW = "enable_snow"
CONF_ENABLE_RAIN = "enable_rain"

# Snow Ratio Configuration (Temp Thresholds in Fahrenheit)
CONF_RATIO_34_PLUS = "ratio_34_plus"
CONF_RATIO_28_34 = "ratio_28_34"
CONF_RATIO_20_28 = "ratio_20_28"
CONF_RATIO_10_20 = "ratio_10_20"
CONF_RATIO_0_10 = "ratio_0_10"
CONF_RATIO_NEG = "ratio_neg"

# Defaults
DEFAULT_NAME = "OWM Precipitation"
DEFAULT_POLLING_INTERVAL = 1  # Hours
DEFAULT_ENABLE_SNOW = True
DEFAULT_ENABLE_RAIN = True

# Default Snow Ratios (Liquid:Snow)
DEFAULT_RATIO_34_PLUS = 10.0
DEFAULT_RATIO_28_34 = 12.0
DEFAULT_RATIO_20_28 = 15.0
DEFAULT_RATIO_10_20 = 20.0
DEFAULT_RATIO_0_10 = 30.0
DEFAULT_RATIO_NEG = 50.0

POLLING_OPTIONS = {
    0.25: "15 Minutes",
    0.5: "30 Minutes",
    1: "1 Hour",
    4: "4 Hours",
    8: "8 Hours",
    12: "12 Hours",
    24: "24 Hours"
}

ATTRIBUTION = "Data provided by OpenWeatherMap"
MANUFACTURER = "OpenWeatherMap"