from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .exceptions import OWMPrecipitationCalculationError


@dataclass(frozen=True)
class SnowRatioConfig:
    below_0f: float
    zero_to_15f: float
    fifteen_to_32f: float
    above_32f: float


class SnowRatioCalculator:
    """Convert liquid precipitation (mm) + temp (°F) to snow inches."""

    def __init__(self, config: Mapping[str, float]) -> None:
        try:
            object.__setattr__(
                self,
                "_config",
                SnowRatioConfig(
                    below_0f=config["below_0f"],
                    zero_to_15f=config["0_to_15f"],
                    fifteen_to_32f=config["15_to_32f"],
                    above_32f=config["above_32f"],
                ),
            )
        except KeyError as exc:
            raise OWMPrecipitationCalculationError(
                f"Missing snow ratio key: {exc}"
            ) from exc

    @property
    def profile(self) -> dict[str, float]:
        cfg = self._config
        return {
            "below_0f": cfg.below_0f,
            "0_to_15f": cfg.zero_to_15f,
            "15_to_32f": cfg.fifteen_to_32f,
            "above_32f": cfg.above_32f,
        }

    def _select_ratio(self, temperature_f: float) -> float:
        cfg = self._config
        if temperature_f < 0:
            return cfg.below_0f
        if temperature_f < 15:
            return cfg.zero_to_15f
        if temperature_f < 32:
            return cfg.fifteen_to_32f
        return cfg.above_32f

    def calculate_snow_inches(
        self, liquid_mm: float, temperature_f: float
    ) -> float:
        """Return snow inches from liquid mm, given temperature."""
        if liquid_mm <= 0:
            return 0.0
        ratio = self._select_ratio(temperature_f)
        if ratio <= 0:
            return 0.0
        mm_per_inch = 25.4
        liquid_inches = liquid_mm / mm_per_inch
        return liquid_inches * ratio
