#!/usr/bin/env python3
"""Check Build 58 release, scheduler and telemetry invariants without networking."""

from pathlib import Path
import plistlib
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[opening : index + 1]
    raise AssertionError(f"Unterminated function: {signature}")


project = (ROOT / "RoamControl.xcodeproj/project.pbxproj").read_text()
assert project.count("CURRENT_PROJECT_VERSION = 58;") == 2
assert project.count("MARKETING_VERSION = 0.9.2;") == 2

with (ROOT / "Configuration/RoamControl-Info.plist").open("rb") as stream:
    info = plistlib.load(stream)
assert info["RoamControlSelfHostedTelemetryEndpoint"].startswith("https://")
assert info["RoamControlSelfHostedTelemetryToken"] == "$(ROAMCONTROL_SELFHOSTED_TELEMETRY_TOKEN)"

public_config = (ROOT / "Configuration/Local.xcconfig").read_text()
assert re.search(r"^ROAMCONTROL_SELFHOSTED_TELEMETRY_TOKEN\s*=\s*$", public_config, re.MULTILINE)
example_config = (ROOT / "Configuration/Local.private.xcconfig.example").read_text()
assert "YOUR-SELF-HOSTED-INGESTION-TOKEN" in example_config

analytics = (ROOT / "RoamControl/Services/UsageAnalyticsService.swift").read_text()
for signature in (
    "func recordActivation(enabled: Bool)",
    "func record(_ event: UsageAnalyticsEvent, enabled: Bool)",
    "func recordFailure(",
):
    body = function_body(analytics, signature)
    assert "guard enabled, destinations.hasConfiguredDestination else { return }" in body

revoke = function_body(analytics, "func revokeLocalIdentity()")
assert "reportingEnabled = false" in revoke
assert "consentRevision += 1" in revoke
assert "pendingRequests.values.forEach { $0.cancel() }" in revoke
assert "preferences.removeObject(forKey: Self.anonymousIdentifierKey)" in revoke

send = function_body(analytics, "private func send(")
assert "self.reportingEnabled" in send
assert "self.consentRevision == revision" in send
assert "async let telemetryDeckSucceeded" in send
assert "async let selfHostedSucceeded" in send

self_hosted_signal = analytics[
    analytics.index("private struct SelfHostedAnalyticsSignal") :
    analytics.index("private struct AnalyticsConfiguration")
]
for required in (
    "locationTaskConfiguration",
    "locationTaskRegistration",
    "pairingTaskConfiguration",
    "pairingTaskRegistration",
    '"location_task_configuration"',
    '"location_task_registration"',
    '"pairing_task_configuration"',
    '"pairing_task_registration"',
):
    assert required in self_hosted_signal

for forbidden in ("latitude", "longitude", "coordinate", "placeName", "route", "pairingRecord", "diagnostic"):
    assert forbidden not in self_hosted_signal

routing_start = analytics.index("let failureContext = failure?.1")
routing_end = analytics.index("guard let data = try? JSONEncoder().encode(payload)", routing_start)
self_hosted_routing = analytics[routing_start:routing_end]

assert "failureContext == .location ? failure?.4?.rawValue : nil" in self_hosted_routing
assert "failureContext == .location ? failure?.5?.rawValue : nil" in self_hosted_routing
assert "failureContext == .pairing ? failure?.4?.rawValue : nil" in self_hosted_routing
assert "failureContext == .pairing ? failure?.5?.rawValue : nil" in self_hosted_routing

session = (ROOT / "RoamControl/Services/Tunnel/LocalDeviceSessionCoordinator.swift").read_text()
submission = function_body(session, "private func submitLocationTask()")
assert "BackgroundTaskIdentifier.configurationStatus(for: \"location\")" in submission
assert "guard taskConfigurationStatus == .permitted," in submission
assert "self.submittedTaskIdentifier == identifier" in submission
assert "!self.cancellationRequested" in submission

pairing = (ROOT / "RoamControl/Services/Pairing/OnDevicePairingCoordinator.swift").read_text()
assert "taskConfigurationStatus: BackgroundTaskConfigurationStatus = .notChecked" in pairing
assert "taskRegistrationStatus: BackgroundTaskRegistrationStatus = .notAttempted" in pairing
assert "taskConfigurationStatus = BackgroundTaskIdentifier.configurationStatus(for: \"pairing\")" in pairing
assert "taskRegistrationStatus = wasRegistered ? .accepted : .rejected" in pairing

app_model = (ROOT / "RoamControl/App/AppModel.swift").read_text()
assert "let includeTaskState = stage == .schedulerRegistration || stage == .schedulerSubmission" in app_model
assert "taskConfigurationStatus: includeTaskState ? self.onDevicePairing.taskConfigurationStatus : nil" in app_model
assert "taskRegistrationStatus: includeTaskState ? self.onDevicePairing.taskRegistrationStatus : nil" in app_model

diagnostics = (ROOT / "RoamControl/Features/Settings/ConnectionHealthView.swift").read_text()
assert "Location task configuration:" in diagnostics
assert "Location task registration:" in diagnostics
assert "Pairing task configuration:" in diagnostics
assert "Pairing task registration:" in diagnostics

private_config = ROOT / "Configuration/Local.private.xcconfig"
if private_config.exists():
    match = re.search(
        r"^ROAMCONTROL_SELFHOSTED_TELEMETRY_TOKEN\s*=\s*(\S+)\s*$",
        private_config.read_text(),
        re.MULTILINE,
    )
    if match and match.group(1):
        token = match.group(1)
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z"], cwd=ROOT
        ).decode().split("\0")
        for relative in filter(None, tracked):
            path = ROOT / relative
            if path.is_file():
                assert token not in path.read_text(errors="ignore"), f"Private token tracked in {relative}"

print("Build 58 release, scheduler and consent-gate source checks passed; no network requests made.")
