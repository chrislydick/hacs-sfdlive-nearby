"""Sensor platform for SFD Live Nearby."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS, DOMAIN
from .coordinator import SfdLiveCoordinator
from .entity import SfdLiveEntity, data_value, incident_at


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SFD Live sensors."""
    coordinator: SfdLiveCoordinator = hass.data[DOMAIN][entry.entry_id]
    count = int(entry.options.get(CONF_MAX_INCIDENTS, entry.data.get(CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS)))
    async_add_entities(
        [
            IncidentCountSensor(coordinator),
            UnitsSensor(coordinator),
            NearestIncidentSensor(coordinator),
            MostRecentIncidentSensor(coordinator),
            *[IncidentDetailSensor(coordinator, index) for index in range(max(count, 0))],
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
            "locations_summary": data.get("locations_summary"),
            "radius_mi": data.get("radius_mi"),
            "incidents": data.get("incidents", []),
            "closest": data.get("closest"),
            "most_recent": data.get("most_recent"),
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
    """Closest active nearby incident."""

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
        nearest = data_value(self.coordinator.data, "closest") or data_value(self.coordinator.data, "nearest")
        if isinstance(nearest, dict):
            return str(nearest.get("location_display") or nearest.get("address") or "unknown location")
        return "none"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        nearest = data_value(self.coordinator.data, "closest") or data_value(self.coordinator.data, "nearest")
        if not isinstance(nearest, dict):
            return {}
        return nearest


class MostRecentIncidentSensor(SfdLiveEntity, SensorEntity):
    """Most recent active nearby incident."""

    entity_description = SensorEntityDescription(
        key="most_recent_incident",
        translation_key="most_recent_incident",
        icon="mdi:clock-alert-outline",
    )

    def __init__(self, coordinator: SfdLiveCoordinator) -> None:
        super().__init__(coordinator, self.entity_description.key)
        self._attr_translation_key = self.entity_description.translation_key

    @property
    def native_value(self) -> str:
        incident = data_value(self.coordinator.data, "most_recent")
        if isinstance(incident, dict):
            return str(incident.get("location_display") or incident.get("address") or "unknown location")
        return "none"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        incident = data_value(self.coordinator.data, "most_recent")
        if not isinstance(incident, dict):
            return {}
        return incident


class IncidentDetailSensor(SfdLiveEntity, SensorEntity):
    """Visible details for one nearby incident slot."""

    entity_description = SensorEntityDescription(
        key="incident_detail",
        translation_key="incident_detail",
        icon="mdi:map-marker-distance",
    )

    def __init__(self, coordinator: SfdLiveCoordinator, index: int) -> None:
        self._index = index
        super().__init__(coordinator, f"incident_detail_{index + 1}")
        self._attr_translation_key = self.entity_description.translation_key
        self._attr_translation_placeholders = {"number": str(index + 1)}

    @property
    def native_value(self) -> str:
        incident = incident_at(self.coordinator.data, self._index)
        if not incident:
            return "none"
        return str(incident.get("location_display") or incident.get("address") or "unknown location")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        incident = incident_at(self.coordinator.data, self._index)
        if not incident:
            return {}
        return {"distance_rank": self._index + 1, **incident}
