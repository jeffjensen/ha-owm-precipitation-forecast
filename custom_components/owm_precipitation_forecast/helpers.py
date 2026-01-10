"""Helper functions for OWM Precipitation Forecast."""

from typing import Any

from .const import (
    CM_TO_INCHES,
    DEFAULT_SNOW_RATIOS,
    INCHES_TO_CM,
)


def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return round(inches * INCHES_TO_CM, 2)


def cm_to_inches(cm: float) -> float:
    """Convert centimeters to inches."""
    return round(cm * CM_TO_INCHES, 2)


def get_snow_ratio_for_temperature(
    temperature_f: float, snow_ratios: dict[str, float] | None = None
) -> float:
    """
    Get the appropriate snow ratio for a given temperature.

    The ratio represents how many inches of snow result from 1 inch of liquid
    precipitation. Higher temperatures produce wetter, heavier snow (lower ratios),
    while lower temperatures produce lighter, fluffier snow (higher ratios).

    Args:
        temperature_f: Temperature in Fahrenheit
        snow_ratios: Optional custom snow ratios. If None, uses defaults.

    Returns:
        Snow ratio (liquid to snow conversion factor)
    """
    ratios = snow_ratios or DEFAULT_SNOW_RATIOS

    # Convert ratio dict keys to floats for comparison
    temp_thresholds = sorted([float(k) for k in ratios.keys()], reverse=True)

    # Find the appropriate ratio based on temperature
    for threshold in temp_thresholds:
        if temperature_f >= threshold:
            return ratios[str(int(threshold))]

    # If temperature is below all thresholds, use the lowest one
    lowest_threshold = str(int(min(temp_thresholds)))
    return ratios[lowest_threshold]


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5 / 9


def sanitize_location_name(name: str) -> str:
    """
    Sanitize location name for use in entity IDs.

    Converts to lowercase, replaces spaces and special characters with underscores.
    """
    # Convert to lowercase
    name = name.lower()

    # Replace spaces and special characters with underscores
    sanitized = ""
    for char in name:
        if char.isalnum():
            sanitized += char
        elif char in (" ", "-", "_"):
            sanitized += "_"

    # Remove consecutive underscores
    while "__" in sanitized:
        sanitized = sanitized.replace("__", "_")

    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")

    return sanitized


def format_entity_name(
    prefix: str, location_name: str, sensor_type: str
) -> str:
    """
    Format entity name with prefix, location, and sensor type.

    Example: owm_precipitation_forecast_home_hourly_rain
    """
    sanitized_location = sanitize_location_name(location_name)
    return f"{prefix}_{sanitized_location}_{sensor_type}"


def round_precipitation(value: float) -> float:
    """Round precipitation value to 2 decimal places."""
    return round(value, 2)


def is_valid_precipitation_value(value: Any) -> bool:
    """Check if a value is a valid precipitation value."""
    if value is None:
        return False

    try:
        float_value = float(value)
        return float_value >= 0
    except (TypeError, ValueError):
        return False


def sum_precipitation(values: list[float]) -> float:
    """Sum precipitation values and round to 2 decimal places."""
    total = sum(v for v in values if is_valid_precipitation_value(v))
    return round_precipitation(total)


def calculate_snow_from_liquid(
    liquid_inches: float,
    temperature_f: float,
    snow_ratios: dict[str, float] | None = None,
) -> float:
    """
    Calculate snow accumulation from liquid precipitation and temperature.

    Args:
        liquid_inches: Liquid precipitation in inches
        temperature_f: Temperature in Fahrenheit
        snow_ratios: Optional custom snow ratios

    Returns:
        Snow accumulation in inches
    """
    if liquid_inches <= 0:
        return 0.0

    ratio = get_snow_ratio_for_temperature(temperature_f, snow_ratios)
    snow_inches = liquid_inches * ratio

    return round_precipitation(snow_inches)


def get_precipitation_description(inches: float) -> str:
    """
    Get a human-readable description of precipitation amount.

    Args:
        inches: Precipitation in inches

    Returns:
        Description string
    """
    if inches == 0:
        return "None"
    if inches < 0.1:
        return "Trace"
    if inches < 0.5:
        return "Light"
    if inches < 1.0:
        return "Moderate"
    if inches < 2.0:
        return "Heavy"
    return "Very Heavy"


def get_precipitation_icon(
    precipitation_type: str, amount: float
) -> str:
    """
    Get appropriate icon for precipitation type and amount.

    Args:
        precipitation_type: "rain" or "snow"
        amount: Precipitation amount in inches

    Returns:
        MDI icon string
    """
    if amount == 0:
        return "mdi:weather-cloudy"

    if precipitation_type == "rain":
        if amount < 0.1:
            return "mdi:weather-rainy"
        elif amount < 0.5:
            return "mdi:weather-rainy"
        elif amount < 1.0:
            return "mdi:weather-pouring"
        else:
            return "mdi:weather-pouring"
    else:  # snow
        if amount < 0.5:
            return "mdi:weather-snowy"
        elif amount < 2.0:
            return "mdi:weather-snowy"
        elif amount < 6.0:
            return "mdi:weather-snowy-heavy"
        else:
            return "mdi:weather-snowy-heavy"


def validate_snow_ratios(ratios: dict[str, float]) -> bool:
    """
    Validate snow ratio configuration.

    Ensures all required temperature thresholds are present and ratios are valid.

    Args:
        ratios: Snow ratio dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    required_temps = ["32", "28", "24", "20", "15", "10", "0", "-10"]

    # Check all required temperatures are present
    for temp in required_temps:
        if temp not in ratios:
            return False

        # Check ratio is a positive number between 5 and 100
        try:
            ratio_value = float(ratios[temp])
            if not (5.0 <= ratio_value <= 100.0):
                return False
        except (TypeError, ValueError):
            return False

    return True
