# Remote 3 Activity Lock

Native Remote 3 `remote-ui` customization adding an optional Activity / Child Lock.

## Planned behavior

- Enable/disable in Remote settings.
- Automatically lock after a configurable inactivity period, independently of standby.
- Optionally lock whenever the remote wakes from standby.
- Unlock with a right-swipe on the touchscreen and/or a full right-swipe on the Remote 3 touch slider.
- Block activity/page navigation while locked while keeping selected physical controls (volume/mute/playback) available.
- Preserve the current activity and page.
- Persist settings locally.
- Validate builds in the Remote 3 simulator before device installation.

## Build model

This repository is an overlay/fork project rather than a Home Assistant integration. The build workflow fetches the upstream `unfoldedcircle/remote-ui` source, applies the Activity Lock patch, and builds the resulting UI.

The upstream project is GPL-3.0-or-later. The original copyright and license headers remain in upstream source files. Our added files are GPL-3.0-or-later.

> **Do not install a build on a physical Remote 3 until the simulator and CI build have passed and the exact target firmware compatibility has been verified.**
