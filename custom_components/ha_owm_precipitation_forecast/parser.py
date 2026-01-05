
from datetime import datetime
from typing import Dict, List
from .model import HourlyPrecipitation, DailyPrecipitation, ForecastBundle
from .snow_ratio import SnowRatioCalculator

def _mm_to_in(mm: float) -> float:
    return mm / 25.4

def parse_forecast(data: Dict, snow_calc: SnowRatioCalculator) -> ForecastBundle:
    hourly: List[HourlyPrecipitation] = []
    daily: List[DailyPrecipitation] = []

    for h in data.get("hourly", []):
        ts = datetime.fromtimestamp(h["dt"])
        rain_mm = h.get("rain", {}).get("1h", 0.0)
        snow_mm = h.get("snow", {}).get("1h", 0.0)
        temp_f = h.get("temp", 32.0)

        rain_in = _mm_to_in(rain_mm)
        snow_liquid_in = _mm_to_in(snow_mm)
        snow_in = snow_calc.liquid_to_snow(snow_liquid_in, temp_f)

        hourly.append(HourlyPrecipitation(ts, rain_in, snow_in))

    for d in data.get("daily", []):
        ts = datetime.fromtimestamp(d["dt"])
        rain_mm = d.get("rain", 0.0)
        snow_mm = d.get("snow", 0.0)
        temp_f = d.get("temp", {}).get("day", 32.0)

        rain_in = _mm_to_in(rain_mm)
        snow_liquid_in = _mm_to_in(snow_mm)
        snow_in = snow_calc.liquid_to_snow(snow_liquid_in, temp_f)

        daily.append(DailyPrecipitation(ts, rain_in, snow_in))

    return ForecastBundle(hourly, daily)
