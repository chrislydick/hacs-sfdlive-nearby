"""Sensor platform for SFD Live Nearby."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SfdLiveCoordinator
from .entity import SfdLiveEntity, data_value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SFD Live sensors."""
    coordinator: SfdLiveCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            IncidentCountSensor(coordinator),
            UnitsSensor(coordinator),
            NearestIncidentSensor(coordinator),
        ]
    )


class IncidentCountSensor(SfdLiveEntity, SensorEntity):
    """Number of active nearby incidents."""

    entity_description = SensorEntityDescription(
        key="nearby_active_incidents",
        translation_key="nearby_active_incidents",
        icon="mdi:fire-alert",
    )

    def __init__(self, coordinator: SfdLiveCoordinator) -> None:
        super().__init__(coordinator, self.entity_description.key)
        self._attr_translation_key = self.entity_description.translation_key

    @property
    def native_value(self) -> int | None:
        return data_value(self.coordinator.data, "active_count")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            "summary": data.get("summary"),
            "radius_mi": data.get("radius_mi"),
            "incidents": data.get("incidents", []),
            "active_seen_in_feed": data.get("active_seen_in_feed"),
            "feed_count": data.get("feed_count"),
            "generated_at": data.get("generated_at"),
            "source_url": data.get("source_url"),
            "error": data.get("error"),
        }


class UnitsSensor(SfdLiveEntity, SensorEntity):
    """Total units assigned to nearby incidents."""

    entity_description = SensorEntityDescription(
        key="nearby_units",
        translation_key="nearby_units",
        icon="mdi:fire-truck",
    )

    def __init__(self, coordinator: SfdLiveCoordinator) -> None:
        super().__init__(coordinator, self.entity_description.key)
        self._attr_translation_key = self.entity_description.translation_key

    @property
    def native_value(self) -> int | None:
        return data_value(self.coordinator.data, "total_units")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {"major_count": data.get("major_count")}


class NearestIncidentSensor(SfdLiveEntity, SensorEntity):
    """Nearest active nearby incident."""

    entity_description = SensorEntityDescription(
        key="nearest_incident",
        translation_key="nearest_incident",
        icon="mdi:map-marker-alert",
    )

    def __init__(self, coordinator: SfdLiveCoordinator) -> None:
        super().__init__(coordinator, self.entity_description.key)
        self._attr_translation_key = self.entity_description.translation_key

    @property
    def native_value(self) -> str:
        nearest = data_value(self.coordinator.data, "nearest")
        if isinstance(nearest, dict):
            return str(nearest.get("label") or "SFD incident")
        return "none"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        nearest = data_value(self.coordinator.data, "nearest")
        if not isinstance(nearest, dict):
            return {}
        return nearest
