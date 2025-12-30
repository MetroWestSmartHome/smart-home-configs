# Greenhouse Temperature Sensor

Low-power ESP32-C3 temperature and humidity sensor using a BME280, integrated with Home Assistant via ESPHome.

## Hardware Required

- Seeed Studio ESP32-C3 (XIAO)
- BME280 sensor (GY-BME280-3.3 variant)
- Dupont cables for prototyping
- Soldering iron for final assembly
- 3D printed case (optional)

See the [full tutorial](https://metrowestsmarthome.com/greenhouse-temperature-sensor/) for product links and detailed instructions.

## Wiring

| BME280 | ESP32-C3 |
|--------|----------|
| VCC | 3.3V |
| GND | GND |
| SCL | GPIO06 |
| SDA | GPIO07 |

## Installation

1. Copy `greenhouse-sensor.yaml` to your ESPHome config folder
2. Update the placeholders with your values
3. Flash to your ESP32-C3
4. Add to Home Assistant

## Full Tutorial

[Greenhouse Temperature Sensor - MetroWest SmartHome](https://metrowestsmarthome.com/greenhouse-temperature-sensor/)
