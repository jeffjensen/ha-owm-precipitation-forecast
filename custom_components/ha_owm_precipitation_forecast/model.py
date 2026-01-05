
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class HourlyPrecipitation:
    timestamp: datetime
    rain_in: float
    snow_in: float

@dataclass(frozen=True)
class DailyPrecipitation:
    date: datetime
    rain_in: float
    snow_in: float

@dataclass(frozen=True)
class ForecastBundle:
    hourly: List[HourlyPrecipitation]
    daily: List[DailyPrecipitation]
