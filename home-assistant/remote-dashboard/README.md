# Universal Remote Dashboard

Control all your TVs and speakers from a single Home Assistant dashboard with automatic device switching and Spotify Connect support.

## Features

- Device dropdown selector at top
- Auto-selects device when media starts playing
- TV remotes: circlepad navigation, volume buttons, keyboard, streaming app buttons
- Speaker remotes: media-control card with playback and volume buttons
- Spotify Connect support: shows Spotify media info when playing on a speaker
- Optional backlight toggle for TVs with LED strips
- Remotes always visible, even when devices are off

## Requirements

- Home Assistant (2024.1 or later)
- [Universal Remote Card](https://github.com/Nerwyn/universal-remote-card) (HACS)
- [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) (HACS, for Now Playing display)
- [custom-brand-icons](https://github.com/elax46/custom-brand-icons) (HACS, optional for streaming app icons)
- Android TV Remote integration (for TV control)
- Google Cast integration (for speaker control)
- Spotify integration (for Spotify Connect support)

## What's Included

- `remote-dashboard.yaml` - Complete dashboard with TV and speaker remotes
- `configuration.yaml` - Input helpers and template sensors
- `automations.yaml` - Auto-select automation

## Important: Entity Selection

For TVs, you likely have multiple media_player entities from different integrations:

- **Cast entity** (e.g., `media_player.living_room_tv`) - Use for **detection sensors**. Reports `playing` state with full media metadata (title, app, artist).
- **Android TV entity** (e.g., `media_player.living_room_tv_2`) - Use for **remote control**. Has `remote.*` entities for sending commands but often only reports `on`/`off` without media info.

The template sensors in `configuration.yaml` should use Cast entities for active device detection and now playing info. The dashboard remote cards should use Android TV entities for control.

## Setup Overview

1. Install required HACS cards (Universal Remote Card, Mushroom Cards)
2. Add the input_select helper from `configuration.yaml`
3. Add the template sensors from `configuration.yaml`
4. Add the automation from `automations.yaml`
5. Create a new dashboard and paste the contents of `remote-dashboard.yaml`
6. Update entity IDs to match your devices (Cast entities for sensors, Android TV for remotes)

## Customization

### Adding More Streaming Apps

The Universal Remote Card has built-in support for many streaming apps. For apps not built-in:

1. Find the Android package name (Settings > Apps on your TV)
2. Create a custom action that launches via `remote.turn_on`
3. Find an icon from MDI or custom-brand-icons (phu prefix)

### Speaker Groups

If you have Chromecast-enabled speakers, you can create speaker groups in the Google Home app. These groups appear as separate media player entities in Home Assistant and can be added to the remote dashboard.

### Spotify Connect

When using Spotify Connect, the Cast speaker entity often shows "off" even while music is playing. The binary sensors in `configuration.yaml` detect when Spotify is playing on each speaker by checking the Spotify entity's `source` attribute. The dashboard then conditionally shows the Spotify media-control card instead of the speaker card.

**Important:** The source names must match exactly what Spotify reports. Check Developer Tools → States → `media_player.spotify_YOUR_USERNAME` while playing on each speaker.

**Future enhancement:** For multiple Spotify accounts, you can convert these binary sensors to template sensors that return which Spotify entity is playing on each speaker.

## Full Tutorial

[Building a Universal Remote Dashboard in Home Assistant - MetroWest SmartHome](https://metrowestsmarthome.com/2025/12/22/home-assistant-remote-dashboard/)
