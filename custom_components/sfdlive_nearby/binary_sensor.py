"""Binary sensor platform for SFD Live Nearby."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SfdLiveCoordinator
from .entity import SfdLiveEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SFD Live binary sensors."""
    coordinator: SfdLiveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ActiveIncidentBinarySensor(coordinator)])


class ActiveIncidentBinarySensor(SfdLiveEntity, BinarySensorEntity):
    """Whether an active SFD incident is within the configured radius."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:fire-alert"
    _attr_translation_key = "active_incident_nearby"

    def __init__(self, coordinator: SfdLiveCoordinator) -> None:
        super().__init__(coordinator, "active_incident_nearby")

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        active_count = data.get("active_count")
        if active_count is None:
            return None
        return int(active_count) > 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "summary": data.get("summary"),
            "radius_mi": data.get("radius_mi"),
            "total_units": data.get("total_units"),
            "major_count": data.get("major_count"),
            "locations_summary": data.get("locations_summary"),
            "nearest": data.get("nearest"),
            "closest": data.get("closest"),
            "most_recent": data.get("most_recent"),
            "incidents": data.get("incidents", []),
        }
