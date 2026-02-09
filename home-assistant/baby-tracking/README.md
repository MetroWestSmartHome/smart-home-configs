# Baby Buddy + Home Assistant Integration

Complete Home Assistant package for baby tracking with Baby Buddy.

## What's Included

This repository contains the **full working configuration** - more comprehensive than the blog post examples.

| File | Description |
|------|-------------|
| `baby_buddy.yaml` | Complete HA package (~1800 lines): REST sensors, template sensors, REST commands, input helpers, scripts, automations |
| `baby_dashboard.yaml` | Full Lovelace dashboard view (~1800 lines): status cards, quick-log buttons, history popups with date navigation, growth charts |
| `import_to_babybuddy.py` | One-time import script for Happiest Baby data migration |

### Configuration Highlights

- **REST sensors** for daily totals and 7-day history
- **Template sensors** for unit conversion (imperial/metric toggle)
- **REST commands** for logging and editing entries from dashboard
- **Input helpers** for quick-log forms and popup triggers
- **Date navigation** for historical browsing with auto-reset to today
- **Popup reset scripts** using Bubble Card's `trigger_entity` pattern
- **External sync automations** for Happiest Baby and Lillio (daycare) - see Source Tags below

### Source Tags

When using automated sync scripts, entries are tagged in the notes field to identify their source:

- `[HB]` - Entry synced from Happiest Baby
- `[LI]` - Entry synced from Lillio (daycare platform)
- No tag - Entry logged manually via dashboard or Baby Buddy app

## Prerequisites

- [Baby Buddy Add-on](https://github.com/OttPeterR/addon-babybuddy) installed
- [Baby Buddy HACS Integration](https://github.com/jcgoette/baby_buddy_homeassistant) configured
- Baby Buddy API key in `secrets.yaml`

## Installation

1. Copy `baby_buddy.yaml` to your `packages/` directory
2. Add to `configuration.yaml`:
   ```yaml
   homeassistant:
     packages:
       baby_buddy: !include packages/baby_buddy.yaml
   ```
3. Update placeholders:
   - `YOUR_HA_IP` → Your Home Assistant IP/hostname
   - `YOUR_BABY` → Your baby's name (lowercase, underscores for entity IDs)
   - `sensor.YOUR_BABY_last_feeding` → Match HACS integration entity IDs
4. Add to `secrets.yaml`:
   ```yaml
   babybuddy_api_token: "Token YOUR_API_KEY_HERE"
   ```
5. Restart Home Assistant

### Dashboard Setup

The dashboard requires these HACS custom cards:
- [Bubble Card](https://github.com/Clooos/Bubble-Card) - Popup cards
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) - Template cards
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) - Charts
- [Layout Card](https://github.com/thomasloven/lovelace-layout-card) - Grid layouts
- [Stack-in-Card](https://github.com/custom-cards/stack-in-card) - Card grouping

To add the dashboard view:
1. Copy contents of `baby_dashboard.yaml`
2. Add to your dashboard YAML under `views:`
3. Replace placeholders:
   - `Your Baby` / `your_baby` → Your baby's name
   - `YOUR_HA_IP` → Your Home Assistant IP/hostname

## Importing Happiest Baby Data

If migrating from Happiest Baby, use the import script:

```bash
# Install dependencies
pip install click requests python-dotenv

# Export from Happiest Baby first (see blog post for exporter tool)

# Import to Baby Buddy
python import_to_babybuddy.py \
    --base-url http://YOUR_HA_IP:8000 \
    --api-key YOUR_API_KEY \
    --data-dir /path/to/exported/csvs \
    --dry-run  # Remove to actually import
```

The script handles:
- All journal types (feedings, diapers, sleep, pumping, growth)
- Timestamp-based duplicate detection (safe to re-run)
- UTC timezone normalization
- Progress logging

## Configuration Notes

### Entity Naming

The HACS Baby Buddy integration creates sensors like `sensor.baby_name_last_feeding`. Replace `YOUR_BABY` in the config with your baby's name (lowercase, underscores).

### Child ID

The config uses `child=1` in API calls. If you have multiple children in Baby Buddy, update this ID accordingly.

### Unit Toggle

The `input_boolean.baby_display_imperial` toggle switches between:
- **On**: oz, lb, in
- **Off**: ml, kg, cm

All template sensors and dashboard displays respect this toggle.

## Full Tutorial

For step-by-step setup instructions, dashboard design patterns, and the Happiest Baby migration guide:

**[Happiest Baby Home Assistant: Migration Guide](https://metrowestsmarthome.com/happiest-baby-home-assistant/)**

The blog covers:
- Exporting data from Happiest Baby (including growth measurements)
- Setting up Baby Buddy add-on and HACS integration
- Building the dashboard with edit popups
- Timezone handling gotchas
- Automated sync setup

## License

MIT License - See [LICENSE](../../LICENSE)
