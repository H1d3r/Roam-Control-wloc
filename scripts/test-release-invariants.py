#!/usr/bin/env python3
"""Check Build 56 release, scheduler and telemetry invariants without networking."""

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
assert project.count("CURRENT_PROJECT_VERSION = 56;") == 2
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
    '"location_task_configuration"',
    '"location_task_registration"',
):
    assert required in self_hosted_signal

for forbidden in ("latitude", "longitude", "coordinate", "placeName", "route", "pairingRecord", "diagnostic"):
    assert forbidden not in self_hosted_signal

session = (ROOT / "RoamControl/Services/Tunnel/LocalDeviceSessionCoordinator.swift").read_text()
submission = function_body(session, "private func submitLocationTask()")
assert "BackgroundTaskIdentifier.configurationStatus(for: identifier)" in submission
assert "guard taskConfigurationStatus == .permitted else" in submission
assert "self.submittedTaskIdentifier == identifier" in submission
assert "!self.cancellationRequested" in submission

diagnostics = (ROOT / "RoamControl/Features/Settings/ConnectionHealthView.swift").read_text()
assert "Location task configuration:" in diagnostics
assert "Location task registration:" in diagnostics

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

print("Build 56 release, scheduler and consent-gate source checks passed; no network requests made.")
