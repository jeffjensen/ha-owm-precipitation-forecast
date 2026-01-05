"""Precipitation calculation utilities."""
from __future__ import annotations

import logging
from typing import Any

from .const import DEFAULT_SNOW_RATIOS, LOGGER_NAME

_LOGGER = logging.getLogger(LOGGER_NAME)


class PrecipitationCalculator:
    """Calculate precipitation with temperature-adjusted snow ratios."""

    # Conversion constants
    MM_TO_INCHES = 0.0393701
    INCHES_TO_CM = 2.54

    def __init__(self, snow_ratios: dict[str, float] | None = None) -> None:
        """Initialize calculator."""
        self.snow_ratios = snow_ratios or DEFAULT_SNOW_RATIOS

    def mm_to_inches(self, mm: float) -> float:
        """Convert millimeters to inches."""
        return mm * self.MM_TO_INCHES

    def inches_to_cm(self, inches: float) -> float:
        """Convert inches to centimeters."""
        return inches * self.INCHES_TO_CM

    def get_snow_ratio(self, temp_f: float) -> float:
        """Get snow ratio based on temperature."""
        if temp_f < 15:
            return self.snow_ratios.get("below_15", 20.0)
        elif temp_f < 20:
            return self.snow_ratios.get("15_to_20", 18.0)
        elif temp_f < 25:
            return self.snow_ratios.get("20_to_25", 15.0)
        elif temp_f < 30:
            return self.snow_ratios.get("25_to_30", 12.0)
        elif temp_f < 32:
            return self.snow_ratios.get("30_to_32", 10.0)
        else:
            return self.snow_ratios.get("above_32", 0.0)

    def mm_to_snow_inches(self, mm: float, temp_f: float) -> float:
        """Convert liquid mm to snow depth in inches with temperature adjustment."""
        if mm <= 0:
            return 0.0

        # Convert mm to inches of liquid
        liquid_inches = self.mm_to_inches(mm)
        
        # Get temperature-adjusted ratio
        ratio = self.get_snow_ratio(temp_f)
        
        # Calculate snow depth
        snow_inches = liquid_inches * ratio
        
        _LOGGER.debug(
            "Snow calculation: %.2fmm @ %.1f°F → %.3f" liquid × %.1f ratio = %.2f" snow",
            mm, temp_f, liquid_inches, ratio, snow_inches
        )
        
        return snow_inches
