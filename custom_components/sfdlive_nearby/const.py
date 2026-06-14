"""Constants for SFD Live Nearby."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "sfdlive_nearby"

CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_MAX_INCIDENTS: Final = "max_incidents"
CONF_NAME: Final = "name"
CONF_RADIUS_MI: Final = "radius_mi"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_MAX_INCIDENTS: Final = 3
DEFAULT_NAME: Final = "SFD Live Nearby"
DEFAULT_RADIUS_MI: Final = 0.5
DEFAULT_SCAN_INTERVAL: Final = 60
DEFAULT_URL: Final = "https://sfdlive.com/api/data/"

PLATFORMS: Final = ["sensor", "binary_sensor", "device_tracker"]
