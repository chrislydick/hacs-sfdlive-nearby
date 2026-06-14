"""Device tracker platform for SFD Live Nearby incident map markers."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS
from .coordinator import SfdLiveCoordinator
from .entity import SfdLiveEntity, incident_at


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up incident device trackers."""
    coordinator: SfdLiveCoordinator = hass.data[DOMAIN][entry.entry_id]
    count = int(entry.options.get(CONF_MAX_INCIDENTS, entry.data.get(CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS)))
    async_add_entities([IncidentTracker(coordinator, index) for index in range(max(count, 0))])


class IncidentTracker(SfdLiveEntity, TrackerEntity):
    """Map marker for a nearby incident."""

    _attr_location_accuracy = 30
    _attr_source_type = SourceType.GPS

    def __init__(self, coordinator: SfdLiveCoordinator, index: int) -> None:
        self._index = index
        super().__init__(coordinator, f"incident_{index + 1}")
        self._attr_translation_key = "incident"
        self._attr_translation_placeholders = {"number": str(index + 1)}

    @property
    def latitude(self) -> float | None:
        incident = incident_at(self.coordinator.data, self._index)
        return incident.get("latitude") if incident else None

    @property
    def longitude(self) -> float | None:
        incident = incident_at(self.coordinator.data, self._index)
        return incident.get("longitude") if incident else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        incident = incident_at(self.coordinator.data, self._index)
        return dict(incident) if incident else {}
