# Remote 3 Activity Lock

Native Remote 3 `remote-ui` customization adding an optional Activity / Child Lock.

## Implemented in the current build overlay

- Enable/disable in Remote settings.
- Configurable inactivity timeout from Off to 30 minutes, independent of standby.
- Optional lock whenever the remote wakes from standby.
- Unlock by right-swipe on the touchscreen.
- Unlock by moving the Remote 3 touch slider to the right.
- Touch slider is repurposed for unlocking while locked; normal slider consumers are suppressed during the lock.
- Activity/page navigation keys are blocked while locked.
- Volume up/down, mute, play/pause and power remain available while locked.
- Current activity and page are not intentionally changed by the lock.
- Settings are stored locally through the existing `Config`/`QSettings` mechanism.
- A safety check prevents activation if both unlock methods are disabled.

## Architecture

This repository is an overlay/fork project rather than a Home Assistant integration. The GitHub Actions workflow fetches a pinned upstream `unfoldedcircle/remote-ui` revision, applies `tools/apply_activity_lock.py`, and builds the resulting UI.

The upstream Remote 3 touch slider already exposes press/move/release events to QML, so the lock does not need to replace the hardware driver. The upstream UI also exposes the central input controller, which is used to block navigation keys while preserving selected physical controls.

## Build status

The desktop build is used as the first QML/C++ compilation gate. An ARM64 build is also produced with Unfolded Circle's currently documented upstream ARM64 toolchain. That ARM64 artifact is explicitly labelled **experimental**: the public upstream build workflow still names its embedded target UCR2, even though Remote 3 uses the same 64-bit ARM architecture. It must not be installed on a physical Remote 3 until the exact firmware/runtime compatibility has been validated in the Remote 3 simulator and on the target firmware.

## Safety

Do not install an experimental binary on a physical Remote 3 yet. First validate the simulator behavior, CI build, custom-UI package format and compatibility with the exact Remote 3 firmware installed on the device.

The upstream project is GPL-3.0-or-later. Original upstream copyright and license headers remain in upstream source files. Added files in this overlay are GPL-3.0-or-later.
