# Rivian Efficiency Tracking for Home Assistant

Track your Rivian's true mi/kWh efficiency with event-based logging, temperature-adjusted baselines, and automatic updates after every trip.

**Full Tutorial:** [Rivian Home Assistant Dashboard: Track Real mi/kWh](https://metrowestsmarthome.com/rivian-home-assistant/)

## Architecture (Updated 2026-01-03)

This uses **event-based logging** instead of querying input_number state history:

- **Events are immutable** - each trip/idle session fires exactly one event
- **No duplicate counting** - SQL queries on events table give accurate totals
- **SOC-based calculation** - `kWh = (SOC_delta / 100) × battery_capacity`
- **Hybrid data retention** - events for 7/30-day accuracy, running totals for lifetime

### Why Events Instead of States?

The original approach queried `input_number` state history, but `input_number` entities can have multiple state records per value (from HA restarts, reloads, sensor polling). This caused duplicate counting - a 5-mile trip could show as 25 miles if there were 5 state records.

Events fire once per occurrence and are immutable.

## Features

- True mi/kWh efficiency from SOC-based battery consumption
- Temperature-band baselines (Cold/Cool/Mild/Warm)
- Mile-weighted averages that improve over time
- Idle drain tracking (kWh/hr while parked)
- Home charging efficiency monitoring
- HA restart protection with in-progress flags
- Accurate 7/30-day stats from event queries
- Lifetime stats from running totals (survive event purge)

## Hardware

- Rivian R1T or R1S
- Home Assistant with [Rivian Integration](https://github.com/bretterer/home-assistant-rivian)
- Optional: Tesla Wall Connector or other smart charger (for charging efficiency)

## Files

| File | Purpose |
|------|---------|
| `configuration.yaml` | Input helpers, SQL sensors, template sensors |
| `automations.yaml` | Trip/idle tracking with event firing |

## Quick Start

1. Install the [Rivian Integration](https://github.com/bretterer/home-assistant-rivian)
2. Copy the input helpers from `configuration.yaml` to your config
3. Copy the SQL sensors (requires `sql:` integration)
4. Copy the automations from `automations.yaml`
5. Update all `YOUR_*` placeholders with your entity names
6. Restart Home Assistant

## Key Entities

After setup, you'll have these sensors:

| Sensor | Description |
|--------|-------------|
| `sensor.rivian_efficiency_last_trip` | Most recent trip's mi/kWh |
| `sensor.rivian_efficiency_7d` | 7-day mile-weighted average |
| `sensor.rivian_efficiency_30d` | 30-day mile-weighted average |
| `sensor.rivian_efficiency_lifetime` | All-time from running totals |
| `sensor.rivian_idle_drain_last` | Last idle drain rate (kWh/hr) |

## Events Fired

The automations fire these custom events:

| Event | Data Fields |
|-------|-------------|
| `rivian_trip_completed` | distance, kwh_used, efficiency, soc_used, temp_band, timestamp |
| `rivian_idle_completed` | kwh_lost, hours_idle, drain_rate, soc_lost, temp_band, timestamp |
| `rivian_charge_completed` | vehicle_kwh, charger_kwh, efficiency_pct, soc_gained, timestamp |

## Temperature Bands

- **Cold**: < 32°F
- **Cool**: 32-50°F
- **Mild**: 50-70°F
- **Warm**: > 70°F

Adjust these thresholds in the automations if needed for your climate.

## Important Notes

- **Do NOT add `initial:` to trip/idle start helpers** - values must persist through HA restarts
- Baseline helpers DO use `initial:` as configuration defaults
- Service mode checks prevent tracking during maintenance
- The `battery_capacity` sensor reports usable capacity (~122 kWh), which fluctuates with degradation

## License

MIT License - See [LICENSE](../../LICENSE)
