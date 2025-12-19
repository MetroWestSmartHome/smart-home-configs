# Mini Split IR Controller

Control IR-only Fujitsu mini splits from Home Assistant using an Athom IR device running ESPHome.

## Hardware Required

- Athom IR Device (or similar ESP-based IR transmitter/receiver)
- IR-controlled mini split (Fujitsu or other supported brand)
- Temperature sensor in same room (thermostat, Ecobee sensor, or BME280)
- Clear line of sight between IR device and mini split

See the [full tutorial](https://metrowestsmarthome.com/2025/02/28/making-simple-mini-splits-smarter/) for product links and detailed instructions.

## Supported Mini Splits

This config uses the `fujitsu_general` platform. For other brands, see [ESPHome IR Climate](https://esphome.io/components/climate/climate_ir) for available platforms.

## Temperature Sensor

The Athom IR device doesn't have a built-in temperature sensor. This config pulls temperature from an existing Home Assistant sensor. Update the `entity_id` to match your room's temperature sensor.

## Installation

1. Flash the Athom device with ESPHome (if it came with Tasmota, see [migration guide](https://esphome.io/guides/migrate_sonoff_tasmota.html))
2. Copy `mini-split-ir.yaml` to your ESPHome config folder
3. Update the placeholders with your values
4. Update the temperature sensor entity_id to match your setup
5. Flash and add to Home Assistant

## Full Tutorial

[Making Simple Mini Splits Smarter - MetroWest SmartHome](https://metrowestsmarthome.com/2025/02/28/making-simple-mini-splits-smarter/)
