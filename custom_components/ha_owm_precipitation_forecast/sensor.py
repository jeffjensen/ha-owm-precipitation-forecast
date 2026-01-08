from __future__ import annotations

from typing import Any
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import SensorEntity

from .coordinator import OWMPrecipitationCoordinator


class OWMPrecipitationSensor(
    CoordinatorEntity[OWMPrecipitationCoordinator], SensorEntity
):
    def __init__(
        self,
        coordinator: OWMPrecipitationCoordinator,
        precip_type: str,
    ) -> None:
        super().__init__(coordinator)
        self._type = precip_type
        self._attr_name = f"OWM {precip_type.capitalize()} Forecast"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self._type)
