# Renogy Solar Monitoring

Monitor your Renogy solar system via BT-1 Bluetooth module and send data to Home Assistant via MQTT.

## Hardware Required

- Raspberry Pi Zero 2 W
- MicroSD card (16GB+ recommended)
- Renogy BT-1 Bluetooth module
- Home Assistant with MQTT broker configured

See the [full tutorial](https://metrowestsmarthome.com/greenhouse-solar-monitoring/) for product links and detailed instructions.

## What's Included

- `mqtt-sensors.yaml` - Home Assistant MQTT sensor configuration for Renogy solar data
- `renogy-config.ini` - Template config for the renogy-bt Python script

## Setup Overview

1. Set up Raspberry Pi with Bluetooth
2. Install [renogy-bt](https://github.com/cyrils/renogy-bt) Python script
3. Configure with your BT-1 device info and MQTT credentials
4. Add the MQTT sensors to Home Assistant
5. Set up cron job for periodic data collection

## Sensors Included

- Solar Power (W)
- Solar Voltage (V)
- Battery SOC (%)
- Battery Voltage (V)
- Daily Solar Generation (Wh)
- Controller Temperature
- Battery Temperature
- Charging Status
- Charging Amp Hours Today
- Total Power Generation (Wh)

## Full Tutorial

[Greenhouse Solar Monitoring - MetroWest SmartHome](https://metrowestsmarthome.com/greenhouse-solar-monitoring/)
