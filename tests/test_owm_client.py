"""Test OWM client."""
import pytest
from aiohttp import ClientError
from aioresponses import aioresponses

from custom_components.ha_owm_precipitation_forecast.const import OWM_API_URL
from custom_components.ha_owm_precipitation_forecast.owm_client import (
    OWMClient,
    OWMClientError,
)


@pytest.mark.asyncio
async def test_client_success(mock_forecast_data: dict) -> None:
    """Test successful API call."""
    with aioresponses() as mock:
        mock.get(OWM_API_URL, payload=mock_forecast_data, status=200)

        client = OWMClient("test_key", 40.7128, -74.0060)
        result = await client.async_get_forecast()

        assert result == mock_forecast_data
        assert "hourly" in result
        assert "daily" in result

        await client.async_close()


@pytest.mark.asyncio
async def test_client_invalid_key() -> None:
    """Test invalid API key."""
    with aioresponses() as mock:
        mock.get(OWM_API_URL, status=401)

        client = OWMClient("invalid_key", 40.7128, -74.0060)

        with pytest.raises(OWMClientError) as exc_info:
            await client.async_get_forecast()

        assert exc_info.value.error_code == "invalid_api_key"
        await client.async_close()


@pytest.mark.asyncio
async def test_client_rate_limited() -> None:
    """Test rate limit error."""
    with aioresponses() as mock:
        mock.get(OWM_API_URL, status=429)

        client = OWMClient("test_key", 40.7128, -74.0060)

        with pytest.raises(OWMClientError) as exc_info:
            await client.async_get_forecast()

        assert exc_info.value.error_code == "rate_limited"
        await client.async_close()


@pytest.mark.asyncio
async def test_client_server_error() -> None:
    """Test server error."""
    with aioresponses() as mock:
        mock.get(OWM_API_URL, status=500)

        client = OWMClient("test_key", 40.7128, -74.0060)

        with pytest.raises(OWMClientError) as exc_info:
            await client.async_get_forecast()

        assert exc_info.value.error_code == "api_unavailable"
        await client.async_close()


@pytest.mark.asyncio
async def test_client_timeout() -> None:
    """Test timeout error."""
    with aioresponses() as mock:
        mock.get(OWM_API_URL, exception=TimeoutError())

        client = OWMClient("test_key", 40.7128, -74.0060)

        with pytest.raises(OWMClientError) as exc_info:
            await client.async_get_forecast()

        assert exc_info.value.error_code == "api_unavailable"
        await client.async_close()


@pytest.mark.asyncio
async def test_client_session_management() -> None:
    """Test client manages session correctly."""
    client = OWMClient("test_key", 40.7128, -74.0060)
    assert client._session is None
    assert client._own_session is True

    await client.async_close()
