"""Pytest fixtures for OWM Precipitation Forecast tests."""
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio


@pytest.fixture
def mock_hass():
    """Mock Home Assistant."""
    hass = Mock()
    hass.config_entries.async_entries.return_value = []
    return hass

@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    entry = Mock()
    entry.data = {"api_key": "test_key", "location": "Test City"}
    return entry

@pytest_asyncio.fixture
def mock_aiohttp_session():
    """Mock aiohttp session."""
    with patch("aiohttp.ClientSession") as mock_session:
        yield mock_session.return_value
    with patch("aiohttp.ClientSession") as mock_session:
        yield mock_session.return_value
