"""Unit tests for API client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from homeassistant.core import HomeAssistant

from custom_components.owm_precipitation_forecast.api_client import OWMApiClient
from custom_components.owm_precipitation_forecast.exceptions import (
    OWMApiConnectionError,
    OWMApiError,
    OWMApiKeyError,
    OWMApiRateLimitError,
    OWMApiResponseError,
    OWMApiTimeoutError,
)


@pytest.mark.unit
class TestAPIClient:
    """Test API client initialization and basic methods."""

    def test_api_client_initialization(self, hass: HomeAssistant):
        """Test API client initialization."""
        client = OWMApiClient("test_api_key", hass)

        assert client.api_key == "test_api_key"
        assert client.hass == hass
        assert client.timeout == 30
        assert client.call_count == 0

    def test_build_url(self, hass: HomeAssistant):
        """Test URL building."""
        client = OWMApiClient("test_key", hass)
        url = client._build_url(45.0, -93.0)

        assert "lat=45.0" in url
        assert "lon=-93.0" in url
        assert "appid=test_key" in url
        assert "units=metric" in url
        assert "exclude=minutely,alerts" in url


@pytest.mark.unit
class TestAPIClientSuccess:
    """Test successful API calls."""

    @pytest.mark.asyncio
    async def test_successful_forecast_fetch(
        self, hass: HomeAssistant, mock_owm_response
    ):
        """Test successful forecast fetch."""
        client = OWMApiClient("test_key", hass)

        with patch.object(client, "_make_request", return_value=mock_owm_response):
            result = await client.get_forecast(45.0, -93.0)

            assert result == mock_owm_response
            assert client.call_count == 1
            assert client.last_call_time is not None

    @pytest.mark.asyncio
    async def test_successful_api_key_validation(self, hass: HomeAssistant, mock_owm_response):
        """Test successful API key validation."""
        client = OWMApiClient("valid_key", hass)

        with patch.object(client, "get_forecast", return_value=mock_owm_response):
            result = await client.validate_api_key()
            assert result is True


@pytest.mark.unit
class TestAPIClientErrors:
    """Test API client error handling."""

    @pytest.mark.asyncio
    async def test_invalid_api_key_error(self, hass: HomeAssistant):
        """Test invalid API key error."""
        client = OWMApiClient("invalid_key", hass)

        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")

        with patch.object(client.session, "get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            with pytest.raises(OWMApiKeyError):
                await client.get_forecast(45.0, -93.0)

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, hass: HomeAssistant):
        """Test rate limit error."""
        client = OWMApiClient("test_key", hass)

        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.text = AsyncMock(return_value="Too Many Requests")

        with patch.object(client.session, "get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            with pytest.raises(OWMApiRateLimitError):
                await client.get_forecast(45.0, -93.0)

    @pytest.mark.asyncio
    async def test_timeout_error(self, hass: HomeAssistant):
        """Test timeout error."""
        client = OWMApiClient("test_key", hass)

        with patch.object(client.session, "get") as mock_get:
            mock_get.side_effect = asyncio.TimeoutError()

            with pytest.raises(OWMApiTimeoutError):
                await client.get_forecast(45.0, -93.0)

    @pytest.mark.asyncio
    async def test_connection_error(self, hass: HomeAssistant):
        """Test connection error."""
        client = OWMApiClient("test_key", hass)

        with patch.object(client.session, "get") as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Connection failed")

            with pytest.raises(OWMApiConnectionError):
                await client.get_forecast(45.0, -93.0)

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, hass: HomeAssistant):
        """Test invalid JSON response."""
        client = OWMApiClient("test_key", hass)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=aiohttp.ContentTypeError(None, None))

        with patch.object(client.session, "get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            with pytest.raises(OWMApiResponseError):
                await client.get_forecast(45.0, -93.0)

    @pytest.mark.asyncio
    async def test_invalid_response_structure(self, hass: HomeAssistant):
        """Test invalid response structure."""
        client = OWMApiClient("test_key", hass)

        invalid_response = {"invalid": "structure"}
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=invalid_response)

        with patch.object(client.session, "get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            with pytest.raises(OWMApiResponseError):
                await client.get_forecast(45.0, -93.0)


@pytest.mark.unit
class TestRetryLogic:
    """Test retry logic and exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self, hass: HomeAssistant, mock_owm_response):
        """Test retry on timeout."""
        client = OWMApiClient("test_key", hass)

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_owm_response)

        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise asyncio.TimeoutError()
            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock()
            return mock_context

        with patch.object(client.session, "get", side_effect=mock_get):
            with patch("asyncio.sleep", return_value=None):
                result = await client.get_forecast(45.0, -93.0)
                assert result == mock_owm_response
                assert call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_auth_error(self, hass: HomeAssistant):
        """Test no retry on authentication error."""
        client = OWMApiClient("invalid_key", hass)

        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")

        call_count = 0

        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_context = MagicMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock()
            return mock_context

        with patch.object(client.session, "get", side_effect=mock_get):
            with pytest.raises(OWMApiKeyError):
                await client.get_forecast(45.0, -93.0)
            
            # Should only be called once, no retries
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, hass: HomeAssistant):
        """Test exponential backoff calculation."""
        client = OWMApiClient("test_key", hass)

        # Test backoff delays
        assert client._calculate_backoff(0) == 1  # 1 * 2^0 = 1
        assert client._calculate_backoff(1) == 2  # 1 * 2^1 = 2
        assert client._calculate_backoff(2) == 4  # 1 * 2^2 = 4

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, hass: HomeAssistant):
        """Test max retries exceeded."""
        client = OWMApiClient("test_key", hass)

        with patch.object(client.session, "get") as mock_get:
            mock_get.side_effect = asyncio.TimeoutError()

            with patch("asyncio.sleep", return_value=None):
                with pytest.raises(OWMApiTimeoutError):
                    await client.get_forecast(45.0, -93.0)


@pytest.mark.unit
class TestResponseValidation:
    """Test response validation."""

    def test_validate_response_valid(self, hass: HomeAssistant, mock_owm_response):
        """Test valid response validation."""
        client = OWMApiClient("test_key", hass)
        assert client._validate_response(mock_owm_response) is True

    def test_validate_response_missing_fields(self, hass: HomeAssistant):
        """Test response validation with missing fields."""
        client = OWMApiClient("test_key", hass)

        # Missing lat
        invalid = {"lon": -93.0, "timezone": "UTC"}
        assert client._validate_response(invalid) is False

        # Missing timezone
        invalid = {"lat": 45.0, "lon": -93.0}
        assert client._validate_response(invalid) is False

    def test_validate_response_no_forecast_data(self, hass: HomeAssistant):
        """Test response validation with no forecast data."""
        client = OWMApiClient("test_key", hass)

        invalid = {"lat": 45.0, "lon": -93.0, "timezone": "UTC"}
        assert client._validate_response(invalid) is False

    def test_validate_response_invalid_forecast_type(self, hass: HomeAssistant):
        """Test response validation with invalid forecast type."""
        client = OWMApiClient("test_key", hass)

        invalid = {
            "lat": 45.0,
            "lon": -93.0,
            "timezone": "UTC",
            "hourly": "not a list",
        }
        assert client._validate_response(invalid) is False


@pytest.mark.unit
class TestCallTracking:
    """Test API call tracking."""

    def test_call_counter_increment(self, hass: HomeAssistant):
        """Test call counter increments."""
        client = OWMApiClient("test_key", hass)

        assert client.call_count == 0
        client._log_successful_call()
        assert client.call_count == 1
        client._log_successful_call()
        assert client.call_count == 2

    def test_last_call_time_updated(self, hass: HomeAssistant):
        """Test last call time is updated."""
        client = OWMApiClient("test_key", hass)

        assert client.last_call_time is None
        client._log_successful_call()
        assert client.last_call_time is not None

    def test_reset_call_count(self, hass: HomeAssistant):
        """Test call count reset."""
        client = OWMApiClient("test_key", hass)

        client._log_successful_call()
        client._log_successful_call()
        assert client.call_count == 2

        client.reset_call_count()
        assert client.call_count == 0
