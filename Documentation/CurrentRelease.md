# Roam Control 0.9.2 - Build 61

Roam Control 0.9.2 Build 61 is the current public release of the source-available SwiftUI app for testing an iPhone's reported location from a clean Apple Maps interface. It supports fixed locations, simulated walking routes, favourites, history and native on-device pairing through LocalDevVPN.

## Before installing

- Requires iOS 27 or newer.
- Requires Developer Mode and LocalDevVPN.
- This is an unsigned IPA. SideStore signs it with the user's own Apple account.
- Intended only for development, quality assurance and responsible testing on a device the user owns and controls.

Read the [installation guide](Installation.md), [privacy explanation](Privacy.md) and [responsible-use policy](ResponsibleUse.md) before using it.

## Download

Download `RoamControl-0.9.2-build61.ipa` from the [Roam Control 0.9.2 release](https://github.com/seanhowarthdev/Roam-Control/releases/tag/v0.9.2).

SHA-256:

`a6dde76eb02a696347be9ccfc3bff34b4a86745c0de7964811363e88fce1890d`

## Highlights

- Search for a place, enter coordinates or tap the map.
- Start and update a fixed reported location without restarting the connection.
- Preview and simulate Apple Maps walking routes.
- Pause, resume, reverse or redirect an active walk.
- Save favourites and revisit recent locations.
- Recover safely after an interrupted session.
- Choose light, dark or automatic appearance and multiple map styles.
- Optionally share a small, fixed set of anonymous usage statistics; sharing is off by default.
- Copy fixed connection and scheduler states for troubleshooting without including location or pairing data in telemetry.

## Build 61 pairing change

Build 61 removes pairing's dependency on successful BGTaskScheduler registration or submission. The RPPairing listener starts directly when a pairing attempt begins, allowing pairing to continue when SideStore re-signing changes the runtime bundle identifier and it no longer matches the permitted background-task identifier in the IPA.

A UIKit background-task assertion covers the brief transition to Settings while pairing. Scheduler configuration remains available for diagnostics, and pairing cleanup still occurs on success, failure, cancellation or timeout.

Build 61 was initially published as a Preview for wider SideStore testing. Following successful real-world testing, it was promoted to the main Roam Control 0.9.2 release.

## Distribution constraints

SideStore and free Apple accounts are subject to Apple's app-count and seven-day refresh limits. Pairing and location sessions require a physical iPhone; the simulator supports interface testing only.

Please report ordinary bugs with the issue template and security problems through a private GitHub security advisory.
