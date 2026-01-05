"""Tests for owm_client.py."""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from aiohttp import ClientError

from custom_components.ha_owm_precipitation_forecast.owm_client import (
    OpenWeatherMapClient,
    OpenWeatherMapError,
)


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initializes correctly."""
    client = OpenWeatherMapClient("test_key", 44.9778, -93.2650)
    assert client.api_key == "test_key"
    assert client.latitude == 44.9778
    assert client.longitude == -93.2650


@pytest.mark.asyncio
async def test_get_forecast_data_success():
    """Test successful forecast data fetch."""
    client = OpenWeatherMapClient("test_key", 44.9778, -93.2650)

    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "hourly": [
            {
                "dt": 1704294000,
                "temp": 28.5,
                "rain": {"1h": 2.5},
                "snow": {"1h": 0.0},
            }
        ],
        "daily": [
            {
                "dt": 1704240000,
                "temp": {"day": 30.0},
                "rain": 5.0,
                "snow": 10.0,
            }
        ],
        "timezone": "America/Chicago",
    })

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        data = await client.get_forecast_data()

        assert "hourly" in data
        assert "daily" in data
        assert "location" in data
        assert len(data["hourly"]) > 0


@pytest.mark.asyncio
async def test_get_forecast_data_invalid_api_key():
    """Test invalid API key handling."""
    client = OpenWeatherMapClient("bad_key", 44.9778, -93.2650)

    mock_response = Mock()
    mock_response.status = 401

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(OpenWeatherMapError, match="Invalid API key"):
            await client.get_forecast_data()


@pytest.mark.asyncio
async def test_get_forecast_data_rate_limit():
    """Test rate limit handling."""
    client = OpenWeatherMapClient("test_key", 44.9778, -93.2650)

    mock_response = Mock()
    mock_response.status = 429

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(OpenWeatherMapError, match="rate limit"):
            await client.get_forecast_data()


@pytest.mark.asyncio
async def test_get_forecast_data_connection_error():
    """Test connection error handling."""
    client = OpenWeatherMapClient("test_key", 44.9778, -93.2650)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = ClientError("Connection failed")

        with pytest.raises(OpenWeatherMapError, match="Connection error"):
            await client.get_forecast_data()


@pytest.mark.asyncio
async def test_validate_credentials():
    """Test credential validation."""
    client = OpenWeatherMapClient("test_key", 44.9778, -93.2650)

    with patch.object(client, "get_forecast_data", AsyncMock()):
        await client.validate_credentials()  # Should not raise


@pytest.mark.asyncio
async def test_close_session():
    """Test session closing."""
    client = OpenWeatherMapClient("test_key", 44.9778, -93.2650)

    # Get session to create it
    session = await client._get_session()
    assert not session.closed

    await client.close()
    # Session closing is handled by aiohttp
