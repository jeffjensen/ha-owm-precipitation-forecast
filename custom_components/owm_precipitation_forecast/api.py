from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from .const import (
    ATTR_RAIN_IN,
    ATTR_SNOW_IN,
    ATTR_TEMP_F,
    ATTR_TEMP_RANGE_F,
    ATTR_SNOW_RATIO_USED,
    ATTR_SNOW_RATIO_PROFILE,
)
from .snow_ratio import SnowRatioCalculator


@dataclass
class HourlyPoint:
    timestamp: datetime
    rain_inches: float
    snow_inches: float
    temperature_f: float
    snow_ratio_used: float


@dataclass
class DailyPoint:
    date: datetime
    rain_inches: float
    snow_inches: float
    temperature_range_f: tuple[float, float]
    snow_ratio_profile: dict[str, float]


class OWMPrecipitationTransformer:
    """Transform OWM raw forecast into normalized precipitation data."""

    def __init__(self, snow_ratio: SnowRatioCalculator) -> None:
        self._snow_ratio = snow_ratio

    @staticmethod
    def _mm_to_inches(mm: float | None) -> float:
        if mm is None or mm <= 0:
            return 0.0
        return mm / 25.4

    @staticmethod
    def _c_to_f(celsius: float) -> float:
        return (celsius * 9 / 5) + 32

    def build_hourly_points(self, hourly: Iterable[dict[str, Any]]) -> list[HourlyPoint]:
        points: list[HourlyPoint] = []
        for item in hourly:
            ts = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
            temp_f = self._c_to_f(item["temp"])
            rain_mm = float(item.get("rain", {}).get("1h", 0.0))
            snow_mm = float(item.get("snow", {}).get("1h", 0.0))

            # Total liquid mm for conversion to snow inches
            liquid_mm = rain_mm + snow_mm
            snow_inches_from_liquid = self._snow_ratio.calculate_snow_inches(
                liquid_mm, temp_f
            )

            # Keep rain as rain-inches-only
            rain_inches = self._mm_to_inches(rain_mm)
            # Use temperature-adjusted snow inches
            snow_inches = snow_inches_from_liquid

            ratio_used = (
                snow_inches_from_liquid / self._mm_to_inches(liquid_mm)
                if liquid_mm > 0
                else 0.0
            )

            points.append(
                HourlyPoint(
                    timestamp=ts,
                    rain_inches=rain_inches,
                    snow_inches=snow_inches,
                    temperature_f=temp_f,
                    snow_ratio_used=ratio_used,
                )
            )
        return points

    def summarize_next24h(self, hourly_points: list[HourlyPoint]) -> dict[str, Any]:
        subset = hourly_points[:24]
        rain_total = sum(p.rain_inches for p in subset)
        snow_total = sum(p.snow_inches for p in subset)
        temps = [p.temperature_f for p in subset] or [0.0]
        ratio_profile = self._snow_ratio.profile
        return {
            ATTR_RAIN_IN: rain_total,
            ATTR_SNOW_IN: snow_total,
            ATTR_TEMP_RANGE_F: (min(temps), max(temps)),
            ATTR_SNOW_RATIO_PROFILE: ratio_profile,
        }

    def summarize_daily(self, daily: Iterable[dict[str, Any]]) -> DailyPoint:
        # Use first daily item as "today"
        item = next(iter(daily))
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
        rain_mm = float(item.get("rain", 0.0))
        snow_mm_raw = float(item.get("snow", 0.0))
        temp_day_c = float(item["temp"]["day"])
        temp_min_c = float(item["temp"]["min"])
        temp_max_c = float(item["temp"]["max"])
        temp_avg_f = self._c_to_f(temp_day_c)

        liquid_mm = rain_mm + snow_mm_raw
        snow_inches = self._snow_ratio.calculate_snow_inches(liquid_mm, temp_avg_f)

        return DailyPoint(
            date=dt,
            rain_inches=self._mm_to_inches(rain_mm),
            snow_inches=snow_inches,
            temperature_range_f=(self._c_to_f(temp_min_c), self._c_to_f(temp_max_c)),
            snow_ratio_profile=self._snow_ratio.profile,
        )
