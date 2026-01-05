import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield

@pytest.fixture
def mock_owm_client():
    with patch("custom_components.owm_precipitation_forecast.api.OWMClient") as mock:
        yield mock

@pytest.fixture
def mock_config_entry():
    entry = AsyncMock()
    entry.data = {
        "api_key": "test_key",
        "location_name": "Home",
        "latitude": 10.0,
        "longitude": 20.0,
        "polling_interval": 1
    }
    entry.options = {}
    entry.entry_id = "test_entry_id"
    return entry