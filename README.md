# SFD Live Nearby

Home Assistant custom integration for nearby Seattle Fire Department incidents from [SFD Live](https://sfdlive.com/).

The integration polls active SFD incidents, filters them around a configured point, and exposes Home Assistant entities for dashboards and automations.

## Entities

- `binary_sensor.<name>_active_incident_nearby`
- `sensor.<name>_nearby_active_incidents`
- `sensor.<name>_nearby_units`
- `sensor.<name>_closest_incident`
- `sensor.<name>_most_recent_incident`
- `sensor.<name>_incident_1_details`
- `sensor.<name>_incident_2_details`
- `sensor.<name>_incident_3_details`
- `device_tracker.<name>_incident_1`
- `device_tracker.<name>_incident_2`
- `device_tracker.<name>_incident_3`

## Install with HACS

1. In Home Assistant, open HACS.
2. Open the three-dot menu and select **Custom repositories**.
3. Add this repository URL as type **Integration**.
4. Download **SFD Live Nearby**.
5. Restart Home Assistant.
6. Go to **Settings > Devices & services > Add integration**.
7. Search for **SFD Live Nearby**.

The setup form defaults to your Home Assistant home coordinates, a `0.5` mile radius, and a `60` second update interval.

## Dashboard

Add the `device_tracker.*_incident_*` entities to a Map card.

For quick readouts, add these sensors to an Entities card:

- Closest incident
- Most recent incident
- Incident 1/2/3 details

The incident detail sensors are sorted by distance. Each one exposes address, distance in miles, dispatch time, unit count, units, response type, SFD Live link, and Google Maps link as attributes.

## Notes

- SFD Live is unofficial and says its incident data is sourced from Seattle Open Data.
- Treat this integration as situational awareness, not as an emergency alerting system.
- The integration uses SFD Live's public web endpoint with browser-style request headers.

## Development

This repo follows the HACS custom integration structure:

```text
custom_components/sfdlive_nearby/
```

No third-party Python requirements are used.
