"""Snow calculation utilities."""

from __future__ import annotations

import logging
from typing import Final

from .const import (
    LOGGER,
    SNOW_RATIO_RANGES,
)

_LOGGER: logging.Logger = LOGGER


class SnowCalculator:
    """Calculate snow accumulation based on precipitation and temperature."""

    def __init__(
        self, base_ratio: float = 10.0, use_temp_adjusted: bool = True
    ) -> None:
        """Initialize the calculator."""
        self.base_ratio = base_ratio
        self.use_temp_adjusted = use_temp_adjusted

    def calculate_snow(
        self, liquid_equivalent: float, temp_celsius: float = 0
    ) -> float:
        """
        Calculate snow from liquid equivalent precipitation.

        Args:
            liquid_equivalent: Rain amount in inches
            temp_celsius: Temperature in Celsius

        Returns:
            Snow amount in inches
        """
        if liquid_equivalent <= 0:
            return 0.0

        ratio = self.get_snow_ratio(temp_celsius)
        return liquid_equivalent * ratio

    def get_snow_ratio(self, temp_celsius: float) -> float:
        """
        Get snow ratio based on temperature.

        Args:
            temp_celsius: Temperature in Celsius

        Returns:
            Snow-to-liquid ratio
        """
        if not self.use_temp_adjusted:
            return self.base_ratio

        # Convert Celsius to Fahrenheit
        temp_fahrenheit = (temp_celsius * 9 / 5) + 32

        # Find appropriate ratio based on temperature range
        for (min_temp, max_temp), ratio in SNOW_RATIO_RANGES.items():
            if min_temp <= temp_fahrenheit < max_temp:
                return ratio

        return self.base_ratio

    def update_base_ratio(self, new_ratio: float) -> None:
        """Update the base snow ratio."""
        self.base_ratio = new_ratio
        _LOGGER.info("Snow ratio updated to %.1f:1", new_ratio)

    def set_temperature_adjusted(self, enabled: bool) -> None:
        """Enable or disable temperature-adjusted ratios."""
        self.use_temp_adjusted = enabled
        _LOGGER.info(
            "Temperature-adjusted ratios %s",
            "enabled" if enabled else "disabled",
        )
