# Build 61: pairing scheduler independence

Build 61 fixes Issue #5 for SideStore-resigned installs. Pairing no longer treats `BGTaskScheduler` configuration, registration, or submission as a prerequisite. The scheduler configuration is still captured in diagnostics, but the RPPairing listener starts directly after the pairing attempt begins.

The native listener and Bonjour publisher remain active while the user follows the normal Settings → Developer Mode → Pair with Host flow. Pairing also requests a UIKit background-task assertion to cover that brief transition; expiration cancels the native session and records the existing timeout failure. The assertion is ended on success, failure, cancellation, or storage completion. No location scheduler or keep-alive behavior changed in this build.

`pairing_task_configuration` remains useful evidence when the runtime bundle identifier does not match the permitted identifier. `pairing_task_registration` is `Not attempted` because pairing deliberately does not register or submit a BG continued-processing task.
