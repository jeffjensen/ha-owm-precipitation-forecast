from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import OWMClient
from .const import (
    ATTR_API_STATUS,
    ATTR_CONSECUTIVE_FAILURES,
    ATTR_LAST_API_ERROR,
    ATTR_LAST_SUCCESSFUL_UPDATE,
    API_STATUS_DEGRADED,
    API_STATUS_FAILED,
    API_STATUS_OK,
    DOMAIN,
)
from .exceptions import OWMPrecipitationAPIError


class OWMPrecipitationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for OWM precipitation data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: OWMClient,
        polling_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            hass.helpers.logger.LoggerAdapter(
                hass.helpers.logger.getLogger(__name__), {}
            ),
            name=DOMAIN,
            update_interval=polling_interval,
        )
        self._client = client
        self._consecutive_failures = 0
        self._last_error: str | None = None
        self._last_successful_update: str | None = None

    @property
    def health(self) -> dict[str, Any]:
        if self._consecutive_failures == 0:
            status = API_STATUS_OK
        elif self._consecutive_failures < 3:
            status = API_STATUS_DEGRADED
        else:
            status = API_STATUS_FAILED
        return {
            ATTR_CONSECUTIVE_FAILURES: self._consecutive_failures,
            ATTR_LAST_API_ERROR: self._last_error,
            ATTR_LAST_SUCCESSFUL_UPDATE: self._last_successful_update,
            ATTR_API_STATUS: status,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self._client.async_get_forecast()
        except OWMPrecipitationAPIError as exc:
            self._consecutive_failures += 1
            self._last_error = str(exc)
            raise UpdateFailed(str(exc)) from exc

        self._consecutive_failures = 0
        self._last_error = None
        self._last_successful_update = self.hass.helpers.event.dt_util.utcnow().isoformat()
        return data
