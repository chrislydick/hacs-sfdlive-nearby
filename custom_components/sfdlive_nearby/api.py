"""SFD Live API client and incident filtering."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession, ClientTimeout

from .const import DEFAULT_URL

REQUEST_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://sfdlive.com/",
    "User-Agent": "HomeAssistant-SFDLiveNearby/0.1",
    "X-Requested-With": "XMLHttpRequest",
}


class SfdLiveError(Exception):
    """Raised when SFD Live data cannot be fetched or parsed."""


@dataclass(frozen=True)
class SfdLiveConfig:
    """Runtime configuration for incident filtering."""

    latitude: float
    longitude: float
    radius_mi: float
    max_incidents: int
    url: str = DEFAULT_URL


class SfdLiveClient:
    """Fetch and filter SFD Live incidents."""

    def __init__(self, session: ClientSession, config: SfdLiveConfig) -> None:
        self._session = session
        self._config = config

    async def async_get_nearby_incidents(self) -> dict[str, Any]:
        """Fetch incidents and return a Home Assistant friendly payload."""
        response = await self._async_fetch()
        rows = response.get("data", [])
        if not isinstance(rows, list):
            raise SfdLiveError("SFD Live response did not contain a data list")

        nearby: list[dict[str, Any]] = []
        active_seen = 0
        for row in rows:
            if not isinstance(row, dict) or not _is_active(row.get("active")):
                continue

            active_seen += 1
            lat = _as_float(row.get("latitude"))
            lon = _as_float(row.get("longitude"))
            if lat is None or lon is None:
                continue

            distance_mi = _miles_between(
                self._config.latitude,
                self._config.longitude,
                lat,
                lon,
            )
            if distance_mi <= self._config.radius_mi:
                nearby.append(_clean_incident(row, distance_mi))

        nearby_by_distance = sorted(nearby, key=lambda item: item["distance_mi"])
        nearby_by_recency = sorted(nearby, key=_incident_datetime_key, reverse=True)
        exposed = nearby_by_distance[: max(self._config.max_incidents, 0)]
        closest = nearby_by_distance[0] if nearby_by_distance else None
        most_recent = nearby_by_recency[0] if nearby_by_recency else None

        return {
            "ok": True,
            "error": None,
            "active_count": len(nearby),
            "total_units": sum(int(item.get("total_units") or 0) for item in nearby),
            "major_count": sum(1 for item in nearby if int(item.get("total_units") or 0) >= 5),
            "nearest": closest,
            "closest": closest,
            "most_recent": most_recent,
            "incidents": exposed,
            "incidents_by_distance": exposed,
            "incidents_by_recency": nearby_by_recency[: max(self._config.max_incidents, 0)],
            "summary": _summary(len(nearby), self._config.radius_mi),
            "locations_summary": _locations_summary(exposed),
            "radius_mi": self._config.radius_mi,
            "home_lat": self._config.latitude,
            "home_lon": self._config.longitude,
            "active_seen_in_feed": active_seen,
            "feed_count": len(rows),
            "feed_meta": response.get("meta") or {},
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_url": self._config.url,
        }

    async def _async_fetch(self) -> dict[str, Any]:
        try:
            async with self._session.get(
                self._config.url,
                headers=REQUEST_HEADERS,
                timeout=ClientTimeout(total=12),
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ClientResponseError) as exc:
            raise SfdLiveError(f"Unable to fetch SFD Live data: {exc}") from exc

        if not isinstance(payload, dict):
            raise SfdLiveError("SFD Live response was not a JSON object")
        return payload


def _miles_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_mi = 3958.7613
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    return radius_mi * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_active(value: Any) -> bool:
    return value is True or value == 1 or value == "1"


def _split_units(units: Any) -> list[str]:
    if not isinstance(units, str):
        return []
    return [unit.strip() for unit in units.split(",") if unit.strip()]


def _incident_datetime_key(incident: dict[str, Any]) -> str:
    value = incident.get("datetime")
    return str(value) if value is not None else ""


def _clean_incident(raw: dict[str, Any], distance_mi: float) -> dict[str, Any]:
    incident_id = raw.get("id")
    lat = _as_float(raw.get("latitude"))
    lon = _as_float(raw.get("longitude"))
    label = raw.get("description_clean") or raw.get("type_clean") or raw.get("type") or "SFD incident"
    units = _split_units(raw.get("units_dispatched"))
    total_units = int(raw.get("total_units_dispatched") or len(units) or 0)

    distance_rounded = round(distance_mi, 3)
    address = raw.get("address")
    return {
        "id": incident_id,
        "incident_number": raw.get("incident_number"),
        "type": raw.get("type"),
        "label": label,
        "description": raw.get("description"),
        "description_clean": raw.get("description_clean"),
        "response_type": raw.get("response_type"),
        "response_mode": raw.get("response_mode"),
        "type_code": raw.get("type_code"),
        "address": address,
        "area": raw.get("area"),
        "battalion": raw.get("battalion"),
        "datetime": raw.get("datetime"),
        "latitude": lat,
        "longitude": lon,
        "distance_mi": distance_rounded,
        "location_display": _location_display(address, distance_rounded),
        "event_display": _event_display(label, address, distance_rounded),
        "total_units": total_units,
        "units": units,
        "units_dispatched": raw.get("units_dispatched"),
        "primary_unit": raw.get("primary_unit"),
        "unit_status": raw.get("unit_status") or {},
        "sfdlive_url": f"https://sfdlive.com/?id={incident_id}" if incident_id is not None else None,
        "map_url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        if lat is not None and lon is not None
        else None,
    }


def _summary(active_count: int, radius_mi: float) -> str:
    if active_count:
        suffix = "s" if active_count != 1 else ""
        return f"{active_count} active SFD incident{suffix} within {radius_mi:g} mi"
    return f"No active SFD incidents within {radius_mi:g} mi"


def _location_display(address: Any, distance_mi: float) -> str:
    if address:
        return f"{address} ({distance_mi:.2f} mi)"
    return f"Unknown location ({distance_mi:.2f} mi)"


def _event_display(label: str, address: Any, distance_mi: float) -> str:
    location = _location_display(address, distance_mi)
    return f"{label} at {location}"


def _locations_summary(incidents: list[dict[str, Any]]) -> str:
    if not incidents:
        return "No active SFD incidents in range"
    return "; ".join(str(incident.get("location_display")) for incident in incidents)
