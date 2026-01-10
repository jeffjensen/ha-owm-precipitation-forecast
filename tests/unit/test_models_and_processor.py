"""Unit tests for models and data processor."""

from datetime import datetime

import pytest

from custom_components.owm_precipitation_forecast.const import DEFAULT_SNOW_RATIOS
from custom_components.owm_precipitation_forecast.data_processor import (
    PrecipitationCalculator,
    determine_precipitation_type,
    extract_daily_data,
    extract_hourly_data,
    is_freezing_temperature,
    validate_forecast_data,
)
from custom_components.owm_precipitation_forecast.models import (
    ApiCallStats,
    DailyForecast,
    ForecastData,
    HealthStatus,
    HourlyForecast,
)


@pytest.mark.unit
class TestHourlyForecast:
    """Test HourlyForecast model."""

    def test_hourly_forecast_creation(self):
        """Test creating hourly forecast."""
        forecast = HourlyForecast(
            timestamp=datetime.now(),
            temperature_f=32.0,
            rain_inches=0.1,
            snow_inches=1.0,
            precipitation_probability=80.0,
        )

        assert forecast.temperature_f == 32.0
        assert forecast.rain_inches == 0.1
        assert forecast.snow_inches == 1.0
        assert forecast.precipitation_probability == 80.0

    def test_hourly_forecast_from_owm_data_rain(self):
        """Test creating hourly forecast from OWM data with rain."""
        owm_data = {
            "dt": int(datetime.now().timestamp()),
            "temp": 10,  # 10°C = 50°F
            "rain": {"1h": 2.54},  # 2.54mm = 0.1 inches
            "pop": 0.8,
        }

        forecast = HourlyForecast.from_owm_data(owm_data, DEFAULT_SNOW_RATIOS)

        assert forecast.temperature_f == 50.0
        assert forecast.rain_inches == 0.1
        assert forecast.snow_inches == 0.0  # Too warm for snow
        assert forecast.precipitation_probability == 80.0

    def test_hourly_forecast_from_owm_data_snow(self):
        """Test creating hourly forecast from OWM data with snow."""
        owm_data = {
            "dt": int(datetime.now().timestamp()),
            "temp": -5,  # -5°C = 23°F
            "rain": {"1h": 2.54},
            "pop": 0.9,
        }

        forecast = HourlyForecast.from_owm_data(owm_data, DEFAULT_SNOW_RATIOS)

        assert forecast.temperature_f == 23.0
        assert forecast.rain_inches == 0.0  # Converted to snow
        assert forecast.snow_inches > 0  # Temperature-adjusted
        assert forecast.precipitation_probability == 90.0


@pytest.mark.unit
class TestDailyForecast:
    """Test DailyForecast model."""

    def test_daily_forecast_creation(self):
        """Test creating daily forecast."""
        forecast = DailyForecast(
            date=datetime.now(),
            temperature_high_f=35.0,
            temperature_low_f=20.0,
            rain_inches=0.5,
            snow_inches=5.0,
            precipitation_probability=70.0,
        )

        assert forecast.temperature_high_f == 35.0
        assert forecast.temperature_low_f == 20.0
        assert forecast.rain_inches == 0.5
        assert forecast.snow_inches == 5.0

    def test_daily_forecast_from_owm_data(self):
        """Test creating daily forecast from OWM data."""
        owm_data = {
            "dt": int(datetime.now().timestamp()),
            "temp": {"max": 10, "min": -5},  # 50°F to 23°F
            "rain": 25.4,  # 25.4mm = 1 inch
            "pop": 0.7,
        }

        forecast = DailyForecast.from_owm_data(owm_data, DEFAULT_SNOW_RATIOS)

        assert forecast.temperature_high_f == 50.0
        assert forecast.temperature_low_f == 23.0
        assert forecast.rain_inches == 1.0
        assert forecast.precipitation_probability == 70.0


@pytest.mark.unit
class TestForecastData:
    """Test ForecastData model."""

    def test_forecast_data_creation(self, sample_forecast_data):
        """Test creating forecast data."""
        assert sample_forecast_data.location_name == "Test Location"
        assert sample_forecast_data.latitude == 45.0
        assert sample_forecast_data.longitude == -93.0
        assert len(sample_forecast_data.hourly_forecasts) == 48
        assert len(sample_forecast_data.daily_forecasts) == 8

    def test_get_hourly_rain_total(self, sample_forecast_data):
        """Test getting hourly rain total."""
        total = sample_forecast_data.get_hourly_rain_total(24)
        assert total == 0.1 * 24  # 24 hours * 0.1 inches each

    def test_get_hourly_snow_total(self, sample_forecast_data):
        """Test getting hourly snow total."""
        total = sample_forecast_data.get_hourly_snow_total(24)
        assert total == 1.0 * 24  # 24 hours * 1.0 inches each

    def test_get_daily_rain_total(self, sample_forecast_data):
        """Test getting daily rain total."""
        total = sample_forecast_data.get_daily_rain_total(7)
        assert total == 0.5 * 7  # 7 days * 0.5 inches each

    def test_get_daily_snow_total(self, sample_forecast_data):
        """Test getting daily snow total."""
        total = sample_forecast_data.get_daily_snow_total(7)
        assert total == 5.0 * 7  # 7 days * 5.0 inches each


@pytest.mark.unit
class TestApiCallStats:
    """Test ApiCallStats model."""

    def test_api_call_stats_creation(self):
        """Test creating API call stats."""
        stats = ApiCallStats(
            total_calls_today=10,
            last_call_time=datetime.now(),
            error_count=0,
            last_error=None,
            last_error_time=None,
        )

        assert stats.total_calls_today == 10
        assert stats.error_count == 0

    def test_increment_calls(self):
        """Test incrementing call counter."""
        stats = ApiCallStats(
            total_calls_today=5,
            last_call_time=datetime.now(),
            error_count=0,
            last_error=None,
            last_error_time=None,
        )

        stats.increment_calls()
        assert stats.total_calls_today == 6
        assert stats.last_call_time is not None

    def test_increment_errors(self):
        """Test incrementing error counter."""
        stats = ApiCallStats(
            total_calls_today=10,
            last_call_time=datetime.now(),
            error_count=0,
            last_error=None,
            last_error_time=None,
        )

        stats.increment_errors("Test error")
        assert stats.error_count == 1
        assert stats.last_error == "Test error"
        assert stats.last_error_time is not None

    def test_reset_daily_stats(self):
        """Test resetting daily statistics."""
        stats = ApiCallStats(
            total_calls_today=100,
            last_call_time=datetime.now(),
            error_count=5,
            last_error="Error",
            last_error_time=datetime.now(),
        )

        stats.reset_daily_stats()
        assert stats.total_calls_today == 0

    def test_should_throttle(self):
        """Test throttle check."""
        stats = ApiCallStats(
            total_calls_today=900,
            last_call_time=datetime.now(),
            error_count=0,
            last_error=None,
            last_error_time=None,
        )

        assert not stats.should_throttle(1000)
        assert stats.should_throttle(900)


@pytest.mark.unit
class TestHealthStatus:
    """Test HealthStatus model."""

    def test_health_status_creation(self):
        """Test creating health status."""
        status = HealthStatus(
            status="ok",
            api_calls_today=10,
            api_calls_remaining=990,
            error_count=0,
            last_error=None,
            last_update=datetime.now(),
            next_update=None,
        )

        assert status.status == "ok"
        assert status.is_healthy
        assert not status.has_errors

    def test_health_status_with_errors(self):
        """Test health status with errors."""
        status = HealthStatus(
            status="error",
            api_calls_today=10,
            api_calls_remaining=990,
            error_count=5,
            last_error="Test error",
            last_update=datetime.now(),
            next_update=None,
        )

        assert status.status == "error"
        assert not status.is_healthy
        assert status.has_errors


@pytest.mark.unit
class TestPrecipitationCalculator:
    """Test PrecipitationCalculator."""

    def test_calculator_creation(self, sample_forecast_data):
        """Test creating precipitation calculator."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        assert calculator.forecast_data == sample_forecast_data

    def test_get_next_24h_rain(self, sample_forecast_data):
        """Test getting next 24h rain."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        total = calculator.get_next_24h_rain()
        assert total == 2.4  # 24 * 0.1

    def test_get_next_24h_snow(self, sample_forecast_data):
        """Test getting next 24h snow."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        total = calculator.get_next_24h_snow()
        assert total == 24.0  # 24 * 1.0

    def test_get_hourly_rain(self, sample_forecast_data):
        """Test getting hourly rain."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        rain = calculator.get_hourly_rain(0)
        assert rain == 0.1

    def test_get_hourly_snow(self, sample_forecast_data):
        """Test getting hourly snow."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        snow = calculator.get_hourly_snow(0)
        assert snow == 1.0

    def test_get_daily_rain(self, sample_forecast_data):
        """Test getting daily rain."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        rain = calculator.get_daily_rain(0)
        assert rain == 0.5

    def test_get_daily_snow(self, sample_forecast_data):
        """Test getting daily snow."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        snow = calculator.get_daily_snow(0)
        assert snow == 5.0

    def test_get_hourly_breakdown_rain(self, sample_forecast_data):
        """Test getting hourly breakdown."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        breakdown = calculator.get_hourly_breakdown_rain(24)

        assert len(breakdown) == 24
        assert "time" in breakdown[0]
        assert "rain" in breakdown[0]
        assert "probability" in breakdown[0]
        assert "temperature" in breakdown[0]

    def test_get_peak_precipitation_time(self, sample_forecast_data):
        """Test getting peak precipitation time."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        peak = calculator.get_peak_precipitation_time("rain", 24)

        assert peak is not None
        assert "time" in peak
        assert "amount" in peak
        assert "probability" in peak

    def test_get_precipitation_summary(self, sample_forecast_data):
        """Test getting precipitation summary."""
        calculator = PrecipitationCalculator(sample_forecast_data)
        summary = calculator.get_precipitation_summary()

        assert "next_24h_rain" in summary
        assert "next_24h_snow" in summary
        assert "next_hour_rain" in summary
        assert "today_rain" in summary
        assert summary["next_24h_rain"] == 2.4


@pytest.mark.unit
class TestDataProcessorHelpers:
    """Test data processor helper functions."""

    def test_validate_forecast_data_valid(self, mock_owm_response):
        """Test validating valid forecast data."""
        assert validate_forecast_data(mock_owm_response)

    def test_validate_forecast_data_missing_fields(self):
        """Test validating invalid forecast data."""
        invalid = {"lat": 45.0}
        assert not validate_forecast_data(invalid)

        invalid = {"lat": 45.0, "lon": -93.0}
        assert not validate_forecast_data(invalid)

    def test_validate_forecast_data_no_forecast(self):
        """Test validating data with no forecast."""
        invalid = {"lat": 45.0, "lon": -93.0, "timezone": "UTC"}
        assert not validate_forecast_data(invalid)

    def test_extract_hourly_data(self, mock_owm_response):
        """Test extracting hourly data."""
        hourly = extract_hourly_data(mock_owm_response, 24)
        assert len(hourly) == 24

    def test_extract_daily_data(self, mock_owm_response):
        """Test extracting daily data."""
        daily = extract_daily_data(mock_owm_response, 7)
        assert len(daily) == 7

    def test_is_freezing_temperature(self):
        """Test freezing temperature check."""
        assert is_freezing_temperature(32)
        assert is_freezing_temperature(0)
        assert is_freezing_temperature(-10)
        assert not is_freezing_temperature(33)
        assert not is_freezing_temperature(50)

    def test_determine_precipitation_type(self):
        """Test determining precipitation type."""
        assert determine_precipitation_type(50, True, False) == "rain"
        assert determine_precipitation_type(20, False, True) == "snow"
        assert determine_precipitation_type(32, True, True) == "mix"
        assert determine_precipitation_type(50, False, False) == "none"
        assert determine_precipitation_type(32, True, False) == "mix"  # Freezing rain
