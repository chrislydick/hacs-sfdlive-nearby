"""Config flow for SFD Live Nearby."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_MAX_INCIDENTS,
    CONF_NAME,
    CONF_RADIUS_MI,
    CONF_SCAN_INTERVAL,
    DEFAULT_MAX_INCIDENTS,
    DEFAULT_NAME,
    DEFAULT_RADIUS_MI,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class SfdLiveNearbyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SFD Live Nearby."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            radius = float(user_input[CONF_RADIUS_MI])
            scan_interval = int(user_input[CONF_SCAN_INTERVAL])
            max_incidents = int(user_input[CONF_MAX_INCIDENTS])
            if radius <= 0:
                errors[CONF_RADIUS_MI] = "positive_number"
            if scan_interval < 30:
                errors[CONF_SCAN_INTERVAL] = "scan_interval_too_low"
            if max_incidents < 1:
                errors[CONF_MAX_INCIDENTS] = "positive_integer"

            if not errors:
                unique_id = f"{float(user_input[CONF_LATITUDE]):.5f}_{float(user_input[CONF_LONGITUDE]):.5f}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=str(user_input[CONF_NAME]),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return SfdLiveNearbyOptionsFlow(config_entry)

    def _schema(self, user_input: dict[str, Any] | None) -> vol.Schema:
        data = user_input or {}
        return vol.Schema(
            {
                vol.Required(CONF_NAME, default=data.get(CONF_NAME, DEFAULT_NAME)): str,
                vol.Required(
                    CONF_LATITUDE,
                    default=data.get(CONF_LATITUDE, self.hass.config.latitude),
                ): float,
                vol.Required(
                    CONF_LONGITUDE,
                    default=data.get(CONF_LONGITUDE, self.hass.config.longitude),
                ): float,
                vol.Required(
                    CONF_RADIUS_MI,
                    default=data.get(CONF_RADIUS_MI, DEFAULT_RADIUS_MI),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_MAX_INCIDENTS,
                    default=data.get(CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS),
                ): vol.Coerce(int),
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.Coerce(int),
            }
        )


class SfdLiveNearbyOptionsFlow(config_entries.OptionsFlow):
    """Handle options for SFD Live Nearby."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            if float(user_input[CONF_RADIUS_MI]) <= 0:
                errors[CONF_RADIUS_MI] = "positive_number"
            if int(user_input[CONF_SCAN_INTERVAL]) < 30:
                errors[CONF_SCAN_INTERVAL] = "scan_interval_too_low"
            if int(user_input[CONF_MAX_INCIDENTS]) < 1:
                errors[CONF_MAX_INCIDENTS] = "positive_integer"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        options = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_RADIUS_MI, default=options.get(CONF_RADIUS_MI, DEFAULT_RADIUS_MI)): vol.Coerce(float),
                    vol.Required(CONF_MAX_INCIDENTS, default=options.get(CONF_MAX_INCIDENTS, DEFAULT_MAX_INCIDENTS)): vol.Coerce(int),
                    vol.Required(CONF_SCAN_INTERVAL, default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): vol.Coerce(int),
                }
            ),
            errors=errors,
        )
