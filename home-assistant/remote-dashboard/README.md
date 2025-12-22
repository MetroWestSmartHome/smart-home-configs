# Universal Remote Dashboard

Control all your TVs and speakers from a single Home Assistant dashboard with automatic device switching.

## Features

- Device dropdown selector at top
- Auto-selects device when media starts playing
- TV remotes: circlepad navigation, volume slider, keyboard, streaming app buttons
- Speaker remotes: media-control card with playback buttons
- Optional backlight toggle for TVs with LED strips
- Remotes always visible, even when devices are off

## Requirements

- Home Assistant (2024.1 or later)
- [Universal Remote Card](https://github.com/Nerwyn/universal-remote-card) (HACS)
- [card-mod](https://github.com/thomasloven/lovelace-card-mod) (HACS, optional for Now Playing marquee)
- [custom-brand-icons](https://github.com/elax46/custom-brand-icons) (HACS, optional for streaming app icons)
- Android TV Remote integration (for TV control)
- Google Cast integration (for speaker control)

## What's Included

- `remote-dashboard.yaml` - Complete dashboard with TV and speaker remotes
- `configuration.yaml` - Input helpers and template sensors
- `automations.yaml` - Auto-select automation

## Setup Overview

1. Install required HACS cards (Universal Remote Card, card-mod)
2. Add the input_select helper from `configuration.yaml`
3. Add the template sensors from `configuration.yaml`
4. Add the automation from `automations.yaml`
5. Create a new dashboard and paste the contents of `remote-dashboard.yaml`
6. Update entity IDs to match your devices

## Customization

### Adding More Streaming Apps

The Universal Remote Card has built-in support for many streaming apps. For apps not built-in:

1. Find the Android package name (Settings > Apps on your TV)
2. Create a custom action that launches via `remote.turn_on`
3. Find an icon from MDI or custom-brand-icons (phu prefix)

### Speaker Groups

If you have Chromecast-enabled speakers, you can create speaker groups in the Google Home app. These groups appear as separate media player entities in Home Assistant and can be added to the remote dashboard.

## Full Tutorial

[Building a Universal Remote Dashboard in Home Assistant - MetroWest SmartHome](https://metrowestsmarthome.com/2025/12/22/home-assistant-remote-dashboard/)
