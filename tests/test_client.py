"""Test OWMClient."""
import pytest
from aiohttp import ClientResponseError
from aioresponses import aioresponses

from custom_components.owm_precipitation_forecast.client import OWMClient, OWMCoordinates
from custom_components.owm_precipitation_forecast.exceptions import OWMPrecipitationAPIError


@pytest.mark.asyncio
async def test_async_get_forecast_success(hass, mock_coords):
    """Test successful API call."""
    client = OWMClient(hass, "valid_key", mock_coords)

    with aioresponses() as m:
        m.get(
            "https://api.openweathermap.org/data/3.0/onecall",
            json={"hourly": [], "daily": []},
            status=200,
        )
        data = await client.async_get_forecast()

    assert "hourly" in data
    assert "daily" in data


@pytest.mark.asyncio
async def test_async_get_forecast_api_error(hass, mock_coords):
    """Test API error response."""
    client = OWMClient(hass, "invalid_key", mock_coords)

    with aioresponses() as m:
        m.get(
            "https://api.openweathermap.org/data/3.0/onecall",
            status=401,
            payload="Invalid API key",
        )
        with pytest.raises(OWMPrecipitationAPIError):
            await client.async_get_forecast()


@pytest.mark.asyncio
async def test_async_get_forecast_timeout(hass, mock_coords):
    """Test timeout error."""
    client = OWMClient(hass, "test_key", mock_coords)

    with aioresponses() as m:
        m.get("https://api.openweathermap.org/data/3.0/onecall", exception=TimeoutError())
        with pytest.raises(OWMPrecipitationAPIError):
            await client.async_get_forecast()


@pytest.mark.asyncio
async def test_async_get_forecast_missing_data(hass, mock_coords):
    """Test missing hourly/daily data."""
    client = OWMClient(hass, "test_key", mock_coords)

    with aioresponses() as m:
        m.get(
            "https://api.openweathermap.org/data/3.0/onecall",
            json={"current": {}},
            status=200,
        )
        with pytest.raises(OWMPrecipitationAPIError):
            await client.async_get_forecast()
