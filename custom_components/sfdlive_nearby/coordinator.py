"""Coordinator for SFD Live Nearby."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import SfdLiveClient, SfdLiveConfig, SfdLiveError
from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_INCIDENTS,
    CONF_RADIUS_MI,
    CONF_SCAN_INTERVAL,
    DEFAULT_MAX_INCIDENTS,
    DEFAULT_RADIUS_MI,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class SfdLiveCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """DataUpdateCoordinator for SFD Live Nearby."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.config_entry = entry
        config = _entry_config(entry)
        self.client = SfdLiveClient(async_get_clientsession(hass), config)
        scan_interval = int(_entry_value(entry, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get_nearby_incidents()
        except SfdLiveError as exc:
            _LOGGER.warning("SFD Live update failed: %s", exc)
            return {
                "ok": False,
                "error": str(exc),
                "active_count": None,
                "total_units": None,
                "major_count": None,
                "nearest": None,
                "incidents": [],
            }


def _entry_config(entry: ConfigEntry) -> SfdLiveConfig:
    return SfdLiveConfig(
        latitude=float(_entry_value(entry, CONF_LATITUDE, 0.0)),
        longitude=float(_entry_value(entry, CONF_LONGITUDE, 0.0)),
        radius_mi=float(_entry_value(entry, CONF_RADIUS_MI, DEFAULT_RADIUS_MI)),
        max_incidents=int(_entry_value(entry, CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS)),
    )


def _entry_value(entry: ConfigEntry, key: str, default: Any) -> Any:
    return entry.options.get(key, entry.data.get(key, default))
