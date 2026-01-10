"""Unit tests for helper functions."""

import pytest

from custom_components.owm_precipitation_forecast.helpers import (
    calculate_snow_from_liquid,
    celsius_to_fahrenheit,
    cm_to_inches,
    fahrenheit_to_celsius,
    format_entity_name,
    get_precipitation_description,
    get_precipitation_icon,
    get_snow_ratio_for_temperature,
    inches_to_cm,
    is_valid_precipitation_value,
    round_precipitation,
    sanitize_location_name,
    sum_precipitation,
    validate_snow_ratios,
)


@pytest.mark.unit
class TestUnitConversions:
    """Test unit conversion functions."""

    def test_inches_to_cm(self):
        """Test inches to centimeters conversion."""
        assert inches_to_cm(1.0) == 2.54
        assert inches_to_cm(2.0) == 5.08
        assert inches_to_cm(0) == 0
        assert inches_to_cm(10) == 25.4

    def test_cm_to_inches(self):
        """Test centimeters to inches conversion."""
        assert cm_to_inches(2.54) == 1.0
        assert cm_to_inches(5.08) == 2.0
        assert cm_to_inches(0) == 0
        assert cm_to_inches(25.4) == 10.0

    def test_celsius_to_fahrenheit(self):
        """Test Celsius to Fahrenheit conversion."""
        assert celsius_to_fahrenheit(0) == 32.0
        assert celsius_to_fahrenheit(100) == 212.0
        assert celsius_to_fahrenheit(-40) == -40.0
        assert celsius_to_fahrenheit(37) == 98.6

    def test_fahrenheit_to_celsius(self):
        """Test Fahrenheit to Celsius conversion."""
        assert fahrenheit_to_celsius(32) == 0.0
        assert fahrenheit_to_celsius(212) == 100.0
        assert fahrenheit_to_celsius(-40) == -40.0
        assert round(fahrenheit_to_celsius(98.6), 1) == 37.0


@pytest.mark.unit
class TestSnowCalculations:
    """Test snow calculation functions."""

    def test_get_snow_ratio_for_temperature(self):
        """Test snow ratio lookup by temperature."""
        # Test exact thresholds
        assert get_snow_ratio_for_temperature(32) == 10.0
        assert get_snow_ratio_for_temperature(28) == 12.0
        assert get_snow_ratio_for_temperature(20) == 20.0
        assert get_snow_ratio_for_temperature(0) == 40.0
        assert get_snow_ratio_for_temperature(-10) == 50.0

        # Test in-between values
        assert get_snow_ratio_for_temperature(35) == 10.0  # Above 32
        assert get_snow_ratio_for_temperature(30) == 12.0  # Between 28-32
        assert get_snow_ratio_for_temperature(22) == 20.0  # Between 20-24
        assert get_snow_ratio_for_temperature(5) == 40.0   # Between 0-10
        assert get_snow_ratio_for_temperature(-20) == 50.0 # Below -10

    def test_calculate_snow_from_liquid(self):
        """Test snow calculation from liquid precipitation."""
        # At 32°F (10:1 ratio)
        assert calculate_snow_from_liquid(1.0, 32) == 10.0
        assert calculate_snow_from_liquid(0.5, 32) == 5.0

        # At 20°F (20:1 ratio)
        assert calculate_snow_from_liquid(1.0, 20) == 20.0
        assert calculate_snow_from_liquid(0.1, 20) == 2.0

        # At 0°F (40:1 ratio)
        assert calculate_snow_from_liquid(1.0, 0) == 40.0

        # Zero liquid
        assert calculate_snow_from_liquid(0, 20) == 0.0

        # Custom ratios
        custom_ratios = {"32": 15.0}
        assert calculate_snow_from_liquid(1.0, 32, custom_ratios) == 15.0


@pytest.mark.unit
class TestNameFormatting:
    """Test name formatting functions."""

    def test_sanitize_location_name(self):
        """Test location name sanitization."""
        assert sanitize_location_name("My House") == "my_house"
        assert sanitize_location_name("Lake-View") == "lake_view"
        assert sanitize_location_name("Cabin #2") == "cabin_2"
        assert sanitize_location_name("  Test  ") == "test"
        assert sanitize_location_name("Multiple   Spaces") == "multiple_spaces"
        assert sanitize_location_name("UPPERCASE") == "uppercase"
        assert sanitize_location_name("Mix_of-Things") == "mix_of_things"

    def test_format_entity_name(self):
        """Test entity name formatting."""
        result = format_entity_name("prefix", "My House", "sensor")
        assert result == "prefix_my_house_sensor"

        result = format_entity_name("owm", "Test Location", "rain")
        assert result == "owm_test_location_rain"


@pytest.mark.unit
class TestPrecipitationHelpers:
    """Test precipitation helper functions."""

    def test_round_precipitation(self):
        """Test precipitation rounding."""
        assert round_precipitation(1.234) == 1.23
        assert round_precipitation(0.999) == 1.0
        assert round_precipitation(0.001) == 0.0
        assert round_precipitation(10.12345) == 10.12

    def test_is_valid_precipitation_value(self):
        """Test precipitation value validation."""
        assert is_valid_precipitation_value(0)
        assert is_valid_precipitation_value(1.5)
        assert is_valid_precipitation_value(100.0)
        assert not is_valid_precipitation_value(-1)
        assert not is_valid_precipitation_value(None)
        assert not is_valid_precipitation_value("invalid")

    def test_sum_precipitation(self):
        """Test precipitation summation."""
        assert sum_precipitation([1.0, 2.0, 3.0]) == 6.0
        assert sum_precipitation([0.5, 0.3, 0.2]) == 1.0
        assert sum_precipitation([]) == 0.0
        assert sum_precipitation([1.234, 2.345]) == 3.58  # Rounded

        # With invalid values
        assert sum_precipitation([1.0, None, 2.0]) == 3.0
        assert sum_precipitation([1.0, -1, 2.0]) == 3.0

    def test_get_precipitation_description(self):
        """Test precipitation description."""
        assert get_precipitation_description(0) == "None"
        assert get_precipitation_description(0.05) == "Trace"
        assert get_precipitation_description(0.25) == "Light"
        assert get_precipitation_description(0.75) == "Moderate"
        assert get_precipitation_description(1.5) == "Heavy"
        assert get_precipitation_description(3.0) == "Very Heavy"

    def test_get_precipitation_icon(self):
        """Test precipitation icon selection."""
        # No precipitation
        assert get_precipitation_icon("rain", 0) == "mdi:weather-cloudy"
        assert get_precipitation_icon("snow", 0) == "mdi:weather-cloudy"

        # Light rain
        assert get_precipitation_icon("rain", 0.1) == "mdi:weather-rainy"
        assert get_precipitation_icon("rain", 0.4) == "mdi:weather-rainy"

        # Heavy rain
        assert get_precipitation_icon("rain", 0.6) == "mdi:weather-pouring"
        assert get_precipitation_icon("rain", 2.0) == "mdi:weather-pouring"

        # Light snow
        assert get_precipitation_icon("snow", 0.3) == "mdi:weather-snowy"
        assert get_precipitation_icon("snow", 1.5) == "mdi:weather-snowy"

        # Heavy snow
        assert get_precipitation_icon("snow", 4.0) == "mdi:weather-snowy-heavy"
        assert get_precipitation_icon("snow", 10.0) == "mdi:weather-snowy-heavy"


@pytest.mark.unit
class TestValidation:
    """Test validation functions."""

    def test_validate_snow_ratios_valid(self):
        """Test snow ratio validation with valid ratios."""
        from custom_components.owm_precipitation_forecast.const import (
            DEFAULT_SNOW_RATIOS,
        )

        assert validate_snow_ratios(DEFAULT_SNOW_RATIOS)

        custom_valid = {
            "32": 10.0,
            "28": 12.0,
            "24": 15.0,
            "20": 20.0,
            "15": 25.0,
            "10": 30.0,
            "0": 40.0,
            "-10": 50.0,
        }
        assert validate_snow_ratios(custom_valid)

    def test_validate_snow_ratios_invalid(self):
        """Test snow ratio validation with invalid ratios."""
        # Missing required temperature
        invalid = {
            "32": 10.0,
            "28": 12.0,
            # Missing other temps
        }
        assert not validate_snow_ratios(invalid)

        # Invalid ratio value (too low)
        invalid = {
            "32": 3.0,  # Below minimum
            "28": 12.0,
            "24": 15.0,
            "20": 20.0,
            "15": 25.0,
            "10": 30.0,
            "0": 40.0,
            "-10": 50.0,
        }
        assert not validate_snow_ratios(invalid)

        # Invalid ratio value (too high)
        invalid = {
            "32": 10.0,
            "28": 120.0,  # Above maximum
            "24": 15.0,
            "20": 20.0,
            "15": 25.0,
            "10": 30.0,
            "0": 40.0,
            "-10": 50.0,
        }
        assert not validate_snow_ratios(invalid)

        # Non-numeric value
        invalid = {
            "32": "invalid",
            "28": 12.0,
            "24": 15.0,
            "20": 20.0,
            "15": 25.0,
            "10": 30.0,
            "0": 40.0,
            "-10": 50.0,
        }
        assert not validate_snow_ratios(invalid)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_extreme_temperatures(self):
        """Test snow calculations at extreme temperatures."""
        # Very hot
        assert get_snow_ratio_for_temperature(100) == 10.0

        # Very cold
        assert get_snow_ratio_for_temperature(-50) == 50.0

        # Calculation with extreme values
        assert calculate_snow_from_liquid(0.1, -50) == 5.0
        assert calculate_snow_from_liquid(10.0, 100) == 100.0

    def test_extreme_precipitation_amounts(self):
        """Test with extreme precipitation amounts."""
        assert round_precipitation(1000.123) == 1000.12
        assert round_precipitation(0.0001) == 0.0
        assert get_precipitation_description(100) == "Very Heavy"

    def test_special_characters_in_names(self):
        """Test location name sanitization with special characters."""
        assert sanitize_location_name("Café") == "caf"
        assert sanitize_location_name("Test@Home") == "test_home"
        assert sanitize_location_name("123 Main St.") == "123_main_st"
        assert sanitize_location_name("___test___") == "test"

    def test_zero_and_negative_values(self):
        """Test handling of zero and negative values."""
        assert is_valid_precipitation_value(0)
        assert not is_valid_precipitation_value(-0.1)
        assert sum_precipitation([0, 0, 0]) == 0.0
        assert calculate_snow_from_liquid(0, 20) == 0.0
