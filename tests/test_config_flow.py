"""Test config flow."""
import pytest
from homeassistant.data_entry_flow import FlowResultType

from custom_components.owm_precipitation_forecast.config_flow import OWMPrecipitationConfigFlow


@pytest.mark.parametrize(
    "input_data,expected_result",
    [
        ({"api_key": "valid", "location_name": "Home", "latitude": "40.7", "longitude": "-74.0"}, FlowResultType.FORM),
        ({"api_key": "invalid", "location_name": "Home", "latitude": "40.7", "longitude": "-74.0"}, FlowResultType.FORM),
    ],
)
async def test_async_step_user(hass, input_data, expected_result):
    """Test user step."""
    result = await hass.config_entries.flow.async_init(
        "owm_precipitation_forecast", context={"source": "user"}, data=input_data
    )

    assert result["type"] == expected_result


@pytest.mark.parametrize(
    "location_name,expected_slug",
    [
        ("My Home", "my_home"),
        ("New York", "new_york"),
        ("St. Louis", "st_louis"),
    ],
)
async def test_slug_generation(location_name, expected_slug):
    """Test location slug generation."""
    from custom_components.owm_precipitation_forecast.config_flow import OWMPrecipitationConfigFlow

    flow = OWMPrecipitationConfigFlow()
    slug = flow._generate_slug(location_name)
    assert slug == expected_slug
