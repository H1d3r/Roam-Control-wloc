# Build 60: background session redesign

Based on the clean private Build 59 source at `bf4eaa5`. Marketing version remains 0.9.2; Debug and Release build numbers are 60.

## Behavior

Location preparation now observes scheduler registration and starts the existing native worker directly. An invalid SideStore-resigned identifier or rejected registration records a recoverable `schedulerRegistration` snapshot and continues. The existing `Connection.RecoveryNeeded` event and `Failure.Observed` companion retain the original configuration, registration, runtime bundle ID and permitted identifiers. All existing diagnostic fields and event definitions remain.

Location BG tasks are no longer submitted. Registration is observed once successfully per process, with its accepted status reused for later sessions. Its callback cannot launch or cancel the location worker. Consequently, location scheduler submission/expiration paths no longer control sessions; pairing scheduler behavior is unchanged. `bgTaskSchedulerAvailable` means registration was accepted, not that submission or background execution is guaranteed. It is false before registration is checked.

An independent Core Location manager starts when the native session reports active, for both fixed and walking sessions. It enables location background updates, disables automatic pauses, uses kilometer accuracy and shows the system background location indicator. It requests When In Use permission when needed. It receives no simulated targets and never stores, uploads or injects received coordinates.

Stop & Restore stops the keep-alive before requesting the existing native cancellation. Native completion, failure and pending-session cleanup also stop it. Permission callbacks after Stop cannot restart it. Denied/restricted permission or service failure is observable and does not abort the foreground simulation; reliable background operation then remains unavailable.

Pairing, LocalDevVPN routing, RPPairing/native code, DVT injection, walking calculations and restoration acknowledgement logic are unchanged. Only scheduler ownership and keep-alive lifecycle wiring changed in the session coordinator.

## Added telemetry

Events: `RoamControl.Background.SchedulerObserved` and `RoamControl.Background.KeepAliveChanged`. Repeated location fixes in the same state do not emit repeated events. All reporting uses the existing opt-in and cancellation gates.

| Meaning | TelemetryDeck field (RoamControl prefix) | Self-hosted JSON field |
| --- | --- | --- |
| Method (`coreLocation`) | backgroundKeepAlive | background_keep_alive |
| Fixed status category | backgroundKeepAliveStatus | background_keep_alive_status |
| Update service requested | backgroundKeepAliveStarted | background_keep_alive_started |
| Location registration accepted | bgTaskSchedulerAvailable | bg_task_scheduler_available |

`starting` means `startUpdatingLocation()` was called; `receivingUpdates` means at least one nonempty update was delivered. Other categories include awaitingAuthorization, denied, restricted, servicesDisabled, missingBackgroundMode, locationUnavailable, failed and stopped. A transient unavailable fix leaves the service requested. These values are captured when an event is created, before asynchronous sending. Diagnostics and the privacy description include the additional information.

## Device acceptance test still required

1. Use the same SideStore installation that produced runtime bundle ID `com.sean.roamcontrol.9THCBUH63A` with the original permitted identifiers. Keep pairing, LocalDevVPN and network conditions unchanged.
2. Start a fixed session. Confirm the same identifier diagnostic remains, disposition is recoverable, and the session becomes active. Confirm system-wide location separately in another app.
3. Confirm keep-alive status changes from starting to receivingUpdates. Background and lock the phone for several minutes; return and verify activity and location persistence.
4. Run Stop & Restore; confirm stopped/false keep-alive diagnostics and independently verify real location returns.
5. Repeat with walking, repeated start/stop, cancellation during connection, permission denied, permission revoked in Settings, and permission granted after stopping while the prompt was open. Verify no late callback restarts the service.
6. With anonymous statistics enabled, verify the self-hosted ingestion service accepts and retains the new fields and event names. With it disabled, verify no traffic. The server implementation is not in this repository, and live ingestion has not been tested or changed.

The offline tests and unsigned compile checks cannot establish on-device background longevity, power use, signing/installation success, or actual location restoration. A granted permission and even delivered updates do not guarantee indefinite iOS execution.

Reference: Apple's [allowsBackgroundLocationUpdates documentation](https://developer.apple.com/documentation/corelocation/cllocationmanager/allowsbackgroundlocationupdates) and [location authorization guidance](https://developer.apple.com/documentation/corelocation/requesting-authorization-to-use-location-services).
