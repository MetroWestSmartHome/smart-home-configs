# Energy Monitoring with rtlamr2mqtt

Read your electric and water meter broadcasts directly into Home Assistant using an RTL-SDR receiver - no meter modifications needed.

## Hardware Required

- RTL-SDR receiver with antenna
- USB extension cable (recommended to reduce interference)
- Home Assistant with MQTT broker configured
- Compatible electric/water meter (see [compatible meters list](https://github.com/bemasher/rtlamr/wiki/Compatible-Meters))

See the [full tutorial](https://metrowestsmarthome.com/2025/04/09/home-assistant-energy-monitoring/) for product links and detailed instructions.

## What's Included

- `rtlamr2mqtt-config.yaml` - Configuration for the rtlamr2mqtt add-on

## Setup Overview

1. Connect RTL-SDR receiver to Home Assistant
2. Install rtlamr2mqtt add-on
3. Configure with `listen_only: true` to find your meter IDs
4. Update config with your meter IDs and protocols
5. Set `listen_only: false` and restart

## Finding Your Meter IDs

1. Set `listen_only: true` in the config
2. Monitor the add-on logs
3. Look for your meter IDs (should match what's on your physical meter)
4. Note the protocol type for each meter

## Full Tutorial

[Monitoring Energy Usage in Home Assistant - MetroWest SmartHome](https://metrowestsmarthome.com/2025/04/09/home-assistant-energy-monitoring/)
