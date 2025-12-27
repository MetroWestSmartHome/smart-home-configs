# Rivian Efficiency Tracking for Home Assistant

Track your Rivian's true mi/kWh efficiency with temperature-adjusted baselines, idle drain monitoring, and automatic updates after every trip.

**Full Tutorial:** [Rivian Home Assistant Dashboard: Track Real mi/kWh](https://metrowestsmarthome.com/rivian-home-assistant/)

## Features

- True mi/kWh efficiency from actual battery consumption (not estimates)
- Temperature-band baselines (Cold/Cool/Mild/Warm)
- Mile-weighted averages that improve over time
- Idle drain tracking (kWh/hr while parked)
- Home charging efficiency monitoring
- HA restart protection with in-progress flags
- Persistent "X ago" timestamps (survives HA restarts)

## Hardware

- Rivian R1T or R1S
- Home Assistant with [Rivian Integration](https://github.com/bretterer/home-assistant-rivian)
- Optional: Tesla Wall Connector or other smart charger (for charging efficiency)

## Files

| File | Purpose |
|------|---------|
| `configuration.yaml` | Input helpers, template sensors, statistics |
| `automations.yaml` | Trip/idle/charge tracking automations |

## Quick Start

1. Install the [Rivian Integration](https://github.com/bretterer/home-assistant-rivian)
2. Copy the input helpers from `configuration.yaml` to your config
3. Copy the automations from `automations.yaml`
4. Update all `YOUR_*` placeholders with your entity names
5. Restart Home Assistant

## Customization

**Temperature Bands:**
- Cold: < 32°F
- Cool: 32-50°F
- Mild: 50-70°F
- Warm: > 70°F

Adjust these thresholds in the automations if needed for your climate.

**Battery Capacity:**
The config uses `sensor.YOUR_RIVIAN_battery_capacity` which reports actual kWh remaining. This automatically accounts for degradation and temperature effects.

## Important Notes

- **Do NOT add `initial:` to trip/idle/charge start helpers** - values must persist through HA restarts
- **Do NOT add `initial:` to end timestamp helpers** - these store actual Unix timestamps for dashboard display
- Baseline helpers DO use `initial:` as configuration defaults
- Service mode checks prevent tracking during maintenance
- End timestamp sensors show "X min/hr/day ago" and survive HA restarts (unlike `last-changed`)

## License

MIT License - See [LICENSE](../../LICENSE)
