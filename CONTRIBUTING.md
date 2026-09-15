# Contributing to Roam Control

Thanks for helping improve Roam Control. Contributions should preserve its narrow purpose: location-based development and testing on an iPhone the user owns and controls.

## Licence and contributor agreement

Roam Control is source available under the licence in `LICENSE`. It is not
open-source software.

The project licence permits private personal modification but does not grant
general permission to redistribute Roam Control, modified versions, patches,
diffs or independent releases.

You may prepare modifications for submission to the official Roam Control
project through its contribution process.

Before a contribution can be accepted or incorporated into Roam Control, the
contributor must read and sign [`CONTRIBUTOR_AGREEMENT.md`](Documentation/Licensing/CONTRIBUTOR_AGREEMENT.md).

The contributor agreement assigns rights in accepted contributions to Sean
Howarth while preserving appropriate contributor authorship credit. This
allows Roam Control to continue to be modified, distributed and licensed as a
single project without giving contributors ownership of the wider Roam Control
codebase.

Opening a pull request by itself does not constitute acceptance or signature
of the contributor agreement. Do not assume that a contribution will be
accepted until the required agreement has been completed.

## Before opening a change

- Search existing issues before creating a duplicate.
- Discuss substantial features in an issue before investing in an implementation.
- Never include pairing records, PINs, certificates, Apple credentials, signing profiles, analytics destinations, exact private locations or diagnostic reports containing personal information.
- Keep optional statistics privacy-preserving, off by default and limited to the documented fixed event set.
- Do not add features intended to bypass access controls, evade enforcement, impersonate another person or misuse a third-party service.

## Development setup

1. Use macOS with Xcode 27 or newer and an iOS 27 SDK.
2. Open `RoamControl.xcodeproj`.
3. Choose your own signing team in Xcode. Do not commit it.
4. Use the simulator for interface work and a physical iPhone for pairing or location-session work.
5. Install and enable LocalDevVPN on the test iPhone.

The prebuilt `RoamPairingFFI.xcframework` allows normal app builds without compiling Rust. If the native bridge changes, follow `Documentation/BuildAndRelease.md` to rebuild both framework slices.

## Pull requests

- Keep each pull request focused.
- Explain the user-visible behaviour and privacy impact.
- Update documentation when a flow or setting changes.
- Complete the relevant rows in `Documentation/RegressionChecklist.md` on a physical iPhone.
- Confirm both Debug and Release configurations compile.
- Do not attach signing material, pairing files or a locally configured `Local.private.xcconfig`.

## Bug reports

Include the Roam Control version/build, iOS version, connection type and reproducible steps. Redact addresses, coordinates, pairing information, Apple IDs, device names and other personal details. Prefer the app's readable diagnostics report over raw internal files.
