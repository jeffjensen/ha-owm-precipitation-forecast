"""Pytest configuration and fixtures for OWM Precipitation Forecast tests."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.owm_precipitation_forecast.const import (
    CONF_ENABLE_RAIN,
    CONF_ENABLE_SNOW,
    CONF_LOCATION_NAME,
    CONF_POLLING_INTERVAL,
    CONF_SNOW_RATIOS,
    DEFAULT_ENABLE_RAIN,
    DEFAULT_ENABLE_SNOW,
    DEFAULT_POLLING_INTERVAL,
    DEFAULT_SNOW_RATIOS,
    DOMAIN,
)


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_API_KEY: "test_api_key_12345",
            CONF_LOCATION_NAME: "Test Location",
            CONF_LATITUDE: 45.0,
            CONF_LONGITUDE: -93.0,
        },
        options={
            CONF_ENABLE_RAIN: DEFAULT_ENABLE_RAIN,
            CONF_ENABLE_SNOW: DEFAULT_ENABLE_SNOW,
            CONF_POLLING_INTERVAL: DEFAULT_POLLING_INTERVAL,
            CONF_SNOW_RATIOS: DEFAULT_SNOW_RATIOS,
        },
        entry_id="test_entry_id",
        title="Test Location",
    )


@pytest.fixture
def mock_owm_response() -> dict:
    """Return a mock OpenWeatherMap API response."""
    base_time = datetime.now()
    
    # Create 48 hours of mock data
    hourly_data = []
    for i in range(48):
        hour_time = base_time + timedelta(hours=i)
        hourly_data.append({
            "dt": int(hour_time.timestamp()),
            "temp": 32 - (i % 24) / 2,  # Temperature varies 32°F to 20°F
            "rain": {"1h": 2.54 if i % 3 == 0 else 0},  # Rain every 3 hours
            "snow": {"1h": 5.08 if i % 5 == 0 else 0},  # Snow every 5 hours
            "pop": 0.8 if i % 2 == 0 else 0.3,  # Alternating probability
        })
    
    # Create 8 days of mock data
    daily_data = []
    for i in range(8):
        day_time = base_time + timedelta(days=i)
        daily_data.append({
            "dt": int(day_time.timestamp()),
            "temp": {
                "max": 35 - i,
                "min": 20 - i,
            },
            "rain": 25.4 if i % 2 == 0 else 0,  # Rain every other day
            "snow": 50.8 if i % 3 == 0 else 0,  # Snow every 3 days
            "pop": 0.7 if i % 2 == 0 else 0.2,
        })
    
    return {
        "lat": 45.0,
        "lon": -93.0,
        "timezone": "America/Chicago",
        "hourly": hourly_data,
        "daily": daily_data,
    }


@pytest.fixture
def mock_owm_response_no_precipitation() -> dict:
    """Return a mock OWM response with no precipitation."""
    base_time = datetime.now()
    
    hourly_data = []
    for i in range(48):
        hour_time = base_time + timedelta(hours=i)
        hourly_data.append({
            "dt": int(hour_time.timestamp()),
            "temp": 65,  # Warm and dry
            "rain": {},
            "snow": {},
            "pop": 0,
        })
    
    daily_data = []
    for i in range(8):
        day_time = base_time + timedelta(days=i)
        daily_data.append({
            "dt": int(day_time.timestamp()),
            "temp": {"max": 70, "min": 55},
            "rain": 0,
            "snow": 0,
            "pop": 0,
        })
    
    return {
        "lat": 45.0,
        "lon": -93.0,
        "timezone": "America/Chicago",
        "hourly": hourly_data,
        "daily": daily_data,
    }


@pytest.fixture
def mock_owm_response_heavy_snow() -> dict:
    """Return a mock OWM response with heavy snow."""
    base_time = datetime.now()
    
    hourly_data = []
    for i in range(48):
        hour_time = base_time + timedelta(hours=i)
        hourly_data.append({
            "dt": int(hour_time.timestamp()),
            "temp": 10,  # Very cold
            "rain": {},
            "snow": {"1h": 25.4},  # Heavy snow every hour
            "pop": 0.95,
        })
    
    daily_data = []
    for i in range(8):
        day_time = base_time + timedelta(days=i)
        daily_data.append({
            "dt": int(day_time.timestamp()),
            "temp": {"max": 15, "min": 5},
            "rain": 0,
            "snow": 254,  # Heavy daily snowfall
            "pop": 0.9,
        })
    
    return {
        "lat": 45.0,
        "lon": -93.0,
        "timezone": "America/Chicago",
        "hourly": hourly_data,
        "daily": daily_data,
    }


@pytest.fixture
def mock_api_client(mock_owm_response):
    """Return a mock API client."""
    with patch(
        "custom_components.owm_precipitation_forecast.api_client.OWMApiClient"
    ) as mock_client:
        client_instance = mock_client.return_value
        client_instance.get_forecast = AsyncMock(return_value=mock_owm_response)
        client_instance.validate_api_key = AsyncMock(return_value=True)
        client_instance.call_count = 0
        client_instance.last_call_time = None
        yield client_instance


@pytest.fixture
def mock_coordinator(hass: HomeAssistant, mock_config_entry, mock_owm_response):
    """Return a mock coordinator with data."""
    from custom_components.owm_precipitation_forecast.coordinator import (
        OWMPrecipitationCoordinator,
    )
    from custom_components.owm_precipitation_forecast.models import ForecastData
    
    coordinator = OWMPrecipitationCoordinator(hass, mock_config_entry)
    
    # Mock the data processing
    coordinator.data = MagicMock(spec=ForecastData)
    coordinator.last_update_success = True
    
    return coordinator


@pytest.fixture
def sample_hourly_forecast():
    """Return a sample hourly forecast."""
    from custom_components.owm_precipitation_forecast.models import HourlyForecast
    
    return HourlyForecast(
        timestamp=datetime.now(),
        temperature_f=32.0,
        rain_inches=0.1,
        snow_inches=1.0,
        precipitation_probability=80.0,
    )


@pytest.fixture
def sample_daily_forecast():
    """Return a sample daily forecast."""
    from custom_components.owm_precipitation_forecast.models import DailyForecast
    
    return DailyForecast(
        date=datetime.now(),
        temperature_high_f=35.0,
        temperature_low_f=20.0,
        rain_inches=0.5,
        snow_inches=5.0,
        precipitation_probability=70.0,
    )


@pytest.fixture
def sample_forecast_data(sample_hourly_forecast, sample_daily_forecast):
    """Return a sample forecast data object."""
    from custom_components.owm_precipitation_forecast.models import ForecastData
    
    return ForecastData(
        location_name="Test Location",
        latitude=45.0,
        longitude=-93.0,
        hourly_forecasts=[sample_hourly_forecast] * 48,
        daily_forecasts=[sample_daily_forecast] * 8,
        last_update=datetime.now(),
        timezone="America/Chicago",
    )


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp client session."""
    with patch("aiohttp.ClientSession") as mock_session:
        session_instance = mock_session.return_value
        session_instance.__aenter__ = AsyncMock(return_value=session_instance)
        session_instance.__aexit__ = AsyncMock(return_value=None)
        yield session_instance


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_setup_entry():
    """Mock setup_entry."""
    with patch(
        "custom_components.owm_precipitation_forecast.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def error_response():
    """Return a mock error response."""
    return {
        "cod": "401",
        "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.",
    }
