# Roam Control 0.9.2 Beta 5 — Build 56

Roam Control 0.9.2 Beta 5 is a source-available SwiftUI app for testing an iPhone's reported location from a clean Apple Maps interface. It supports fixed locations, simulated walking routes, favourites, history and native on-device pairing through LocalDevVPN.

## Before installing

- Requires iOS 27 or newer.
- Requires Developer Mode and LocalDevVPN.
- This is an unsigned IPA. SideStore signs it with the user's own Apple account.
- Intended only for development, quality assurance and responsible testing on a device the user owns and controls.

Read the [installation guide](Installation.md), [privacy explanation](Privacy.md) and [responsible-use policy](ResponsibleUse.md) before using it.

## Download

Attach the verified `RoamControl-0.9.2-build56.ipa` only after the Release build and IPA packaging checks, SideStore installation and regression checks pass. Record the final SHA-256 checksum with the release asset; do not copy a checksum from an earlier build.

## Highlights

- Search for a place, enter coordinates or tap the map.
- Start and update a fixed reported location without restarting the connection.
- Preview and simulate Apple Maps walking routes.
- Pause, resume, reverse or redirect an active walk.
- Save favourites and revisit recent locations.
- Recover safely after an interrupted session.
- Choose light, dark or automatic appearance and multiple map styles.
- Optionally share a small, fixed set of anonymous usage counts; sharing is off by default.
- Copy fixed location-task configuration and registration states for troubleshooting without including identifiers or diagnostics in telemetry.

## Known distribution constraints

SideStore and free Apple accounts are subject to Apple's app-count and seven-day refresh limits. Pairing and location sessions require a physical iPhone; the simulator supports interface testing only.

This beta is provided without warranty. Please report ordinary bugs with the issue template and security problems through a private GitHub security advisory.

## Validation note

Build 54 was a private location-task diagnostic build with limited external validation. Beta 5 carries forward bounded registration validation and diagnostics, but no claim is made that these changes resolve every iOS scheduler-registration failure.

## Licensing note

Roam Control 0.9.0 Beta 1 remains available under its original MIT Licence. Beta 5 uses the licence stated in the repository's current `LICENSE` file.
