import pytest
from custom_components.owm_precipitation_forecast.api import OWMClient
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_get_forecast_success():
    session = AsyncMock()
    response = AsyncMock()
    response.json.return_value = {"lat": 10, "lon": 20}
    session.get.return_value.__aenter__.return_value = response

    client = OWMClient("key", session)
    data = await client.get_forecast(10, 20)
    assert data["lat"] == 10