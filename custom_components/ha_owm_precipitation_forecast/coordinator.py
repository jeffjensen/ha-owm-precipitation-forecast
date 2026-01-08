from __future__ import annotations
from typing import Any
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from .owm_client import OWMClient

_LOGGER = logging.getLogger(__name__)

class OWMForecastCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, client: OWMClient, update_interval: int):
        super().__init__(
            hass,
            _LOGGER,
            name="OWM Precipitation Forecast Coordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self._client = client
        self.last_error: str | None = None

    async def _async_update_data(self) -> dict[str, float]:
        try:
            self.last_error = None
            return await self._client.async_get_forecast()
        except Exception as err:
            self.last_error = str(err)
            raise UpdateFailed(err) from err
