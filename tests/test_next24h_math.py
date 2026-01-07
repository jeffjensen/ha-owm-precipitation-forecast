from datetime import datetime
from custom_components.ha_owm_precipitation_forecast.models import HourlyPrecip, ForecastData

def test_next24h_rollup():
    hours = [
        HourlyPrecip(datetime.utcnow(), rain_in=0.1, snow_in=0.2)
        for _ in range(30)
    ]
    data = ForecastData(hourly=hours, daily=[])
    assert sum(h.rain_in for h in data.hourly[:24]) == 2.4
    assert sum(h.snow_in for h in data.hourly[:24]) == 4.8
