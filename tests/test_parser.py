
from custom_components.ha_owm_precipitation_forecast.snow_ratio import SnowRatioCalculator
from custom_components.ha_owm_precipitation_forecast.parser import parse_forecast

def test_basic_parse():
    calc = SnowRatioCalculator({32.0: 10.0})
    data = {
        "hourly": [{"dt": 0, "temp": 30.0, "rain": {"1h": 2.54}, "snow": {"1h": 0.0}}],
        "daily": [{"dt": 0, "temp": {"day": 28.0}, "rain": 0.0, "snow": 2.54}],
    }
    bundle = parse_forecast(data, calc)
    assert round(bundle.hourly[0].rain_in, 2) == 0.10
    assert round(bundle.daily[0].snow_in, 2) == 1.0
