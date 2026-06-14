"""Base entities for SFD Live Nearby."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SfdLiveCoordinator


class SfdLiveEntity(CoordinatorEntity[SfdLiveCoordinator]):
    """Base class for SFD Live entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SfdLiveCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        entry = self.coordinator.config_entry
        return DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="SFD Live",
            name=entry.title,
            configuration_url="https://sfdlive.com/",
        )

    @property
    def available(self) -> bool:
        data: dict[str, Any] = self.coordinator.data or {}
        return bool(data.get("ok"))


def data_value(data: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if not data:
        return default
    return data.get(key, default)


def incident_at(data: dict[str, Any] | None, index: int) -> dict[str, Any] | None:
    incidents = data_value(data, "incidents", [])
    if isinstance(incidents, list) and len(incidents) > index and isinstance(incidents[index], dict):
        return incidents[index]
    return None
