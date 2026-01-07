from __future__ import annotations
from typing import Dict

class SnowRatioCalculator:
    def __init__(self, ratios: Dict[float, float]):
        # ratios: temp_f -> ratio, sorted descending temp
        self._ratios = dict(sorted(ratios.items(), reverse=True))

    def ratio_for_temp(self, temp_f: float) -> float:
        for threshold, ratio in self._ratios.items():
            if temp_f >= threshold:
                return ratio
        return list(self._ratios.values())[-1]

    def liquid_to_snow_inches(self, liquid_in: float, temp_f: float) -> float:
        return liquid_in * self.ratio_for_temp(temp_f)
