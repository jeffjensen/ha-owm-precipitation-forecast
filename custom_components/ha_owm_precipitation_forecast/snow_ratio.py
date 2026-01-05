
from typing import Dict

class SnowRatioCalculator:
    def __init__(self, ratios: Dict[float, float]):
        self._ratios = dict(sorted(ratios.items()))

    def ratio_for_temp_f(self, temp_f: float) -> float:
        for threshold, ratio in self._ratios.items():
            if temp_f <= threshold:
                return ratio
        return list(self._ratios.values())[-1]

    def liquid_to_snow(self, liquid_in: float, temp_f: float) -> float:
        return liquid_in * self.ratio_for_temp_f(temp_f)
