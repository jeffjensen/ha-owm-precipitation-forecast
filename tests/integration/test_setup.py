"""Integration tests for complete setup flow."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.owm_precipitation_forecast.const import DOMAIN


@pytest.mark.integration
class TestIntegrationSetup:
    """Test complete integration setup."""

    async def test_full_integration_setup(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test full integration setup flow."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            # Verify entry state
            assert mock_config_entry.state == ConfigEntryState.LOADED

    async def test_integration_creates_sensors(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test integration creates all expected sensors."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            entity_reg = er.async_get(hass)
            entities = er.async_entries_for_config_entry(
                entity_reg, mock_config_entry.entry_id
            )

            # Should have 7 sensors (6 precipitation + 1 health)
            assert len(entities) == 7

            # Verify entity IDs
            entity_ids = [e.entity_id for e in entities]
            assert any("hourly_rain" in e_id for e_id in entity_ids)
            assert any("hourly_snow" in e_id for e_id in entity_ids)
            assert any("daily_rain" in e_id for e_id in entity_ids)
            assert any("daily_snow" in e_id for e_id in entity_ids)
            assert any("next24h_rain" in e_id for e_id in entity_ids)
            assert any("next24h_snow" in e_id for e_id in entity_ids)
            assert any("health" in e_id for e_id in entity_ids)

    async def test_integration_unload(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test integration unloads cleanly."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.LOADED

            # Unload
            await hass.config_entries.async_unload(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.NOT_LOADED

    async def test_integration_reload(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test integration reload."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.LOADED

            # Reload
            await hass.config_entries.async_reload(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.LOADED


@pytest.mark.integration
class TestSensorStates:
    """Test sensor states after setup."""

    async def test_sensors_have_correct_states(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test sensors have correct states after setup."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            # Check hourly rain sensor
            state = hass.states.get("sensor.owm_precipitation_forecast_test_location_hourly_rain")
            assert state is not None
            assert float(state.state) >= 0

            # Check health sensor
            health_state = hass.states.get("sensor.owm_precipitation_forecast_test_location_health")
            assert health_state is not None
            assert health_state.state in ["ok", "warning", "error", "unavailable"]

    async def test_sensors_have_attributes(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test sensors have proper attributes."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            state = hass.states.get("sensor.owm_precipitation_forecast_test_location_hourly_rain")
            assert state is not None
            
            attributes = state.attributes
            assert "location" in attributes
            assert "coordinates" in attributes
            assert attributes["location"] == "Test Location"


@pytest.mark.integration
class TestServiceCalls:
    """Test service calls."""

    async def test_update_forecast_service(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test update_forecast service call."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ) as mock_get:
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            initial_call_count = mock_get.call_count

            # Call update service
            await hass.services.async_call(
                DOMAIN,
                "update_forecast",
                {},
                blocking=True,
            )

            # Should have made an additional API call
            assert mock_get.call_count > initial_call_count

    async def test_clear_errors_service(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test clear_errors service call."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            # Call clear errors service
            await hass.services.async_call(
                DOMAIN,
                "clear_errors",
                {},
                blocking=True,
            )

            # Service should complete without error
            # Actual error clearing is tested in unit tests


@pytest.mark.integration
class TestOptionsFlowIntegration:
    """Test options flow integration."""

    async def test_changing_options_reloads_integration(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test changing options reloads integration."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.LOADED

            # Change options
            hass.config_entries.async_update_entry(
                mock_config_entry,
                options={
                    **mock_config_entry.options,
                    "enable_rain": False,
                },
            )

            # Trigger options update
            await hass.config_entries.async_reload(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.LOADED


@pytest.mark.integration
class TestMultipleLocations:
    """Test multiple location configurations."""

    async def test_multiple_locations_independent(
        self, hass: HomeAssistant, mock_owm_response
    ):
        """Test multiple locations operate independently."""
        from pytest_homeassistant_custom_component.common import MockConfigEntry

        entry1 = MockConfigEntry(
            domain=DOMAIN,
            data={
                "api_key": "key1",
                "location_name": "Location 1",
                "latitude": 45.0,
                "longitude": -93.0,
            },
            options={
                "enable_rain": True,
                "enable_snow": True,
                "polling_interval": 3600,
            },
        )

        entry2 = MockConfigEntry(
            domain=DOMAIN,
            data={
                "api_key": "key2",
                "location_name": "Location 2",
                "latitude": 40.0,
                "longitude": -75.0,
            },
            options={
                "enable_rain": True,
                "enable_snow": False,  # Different options
                "polling_interval": 3600,
            },
        )

        entry1.add_to_hass(hass)
        entry2.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_setup(entry1.entry_id)
            await hass.config_entries.async_setup(entry2.entry_id)
            await hass.async_block_till_done()

            # Both should be loaded
            assert entry1.state == ConfigEntryState.LOADED
            assert entry2.state == ConfigEntryState.LOADED

            # Check entities created for location 1 (7 sensors)
            entity_reg = er.async_get(hass)
            entities1 = er.async_entries_for_config_entry(entity_reg, entry1.entry_id)
            assert len(entities1) == 7

            # Check entities created for location 2 (4 sensors: 3 rain + 1 health, no snow)
            entities2 = er.async_entries_for_config_entry(entity_reg, entry2.entry_id)
            assert len(entities2) == 4  # Only rain sensors + health


@pytest.mark.integration
class TestErrorRecovery:
    """Test error recovery in integration."""

    async def test_integration_setup_failure_with_invalid_api_key(
        self, hass: HomeAssistant, mock_config_entry
    ):
        """Test integration handles setup failure gracefully."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            side_effect=Exception("Invalid API key"),
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            # Should be in error state (SETUP_ERROR)
            assert mock_config_entry.state == ConfigEntryState.SETUP_ERROR

    async def test_integration_recovers_after_api_key_fix(
        self, hass: HomeAssistant, mock_config_entry, mock_owm_response
    ):
        """Test integration recovers after fixing API key."""
        mock_config_entry.add_to_hass(hass)

        # First attempt fails
        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            side_effect=Exception("Invalid API key"),
        ):
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.SETUP_ERROR

        # Retry with valid API key
        with patch(
            "custom_components.owm_precipitation_forecast.api_client.OWMApiClient.get_forecast",
            return_value=mock_owm_response,
        ):
            await hass.config_entries.async_reload(mock_config_entry.entry_id)
            await hass.async_block_till_done()

            assert mock_config_entry.state == ConfigEntryState.LOADED
