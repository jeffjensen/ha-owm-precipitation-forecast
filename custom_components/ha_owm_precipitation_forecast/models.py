from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class HourlyPrecip:
    timestamp: datetime
    rain_in: float
    snow_in: float

@dataclass(frozen=True)
class DailyPrecip:
    date: datetime
    rain_in: float
    snow_in: float

@dataclass(frozen=True)
class ForecastData:
    hourly: list[HourlyPrecip]
    daily: list[DailyPrecip]
