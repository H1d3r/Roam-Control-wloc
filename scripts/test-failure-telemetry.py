#!/usr/bin/env python3
"""Run production preflight observers, telemetry routing and JSON encoding offline.

Extract bounded production bodies; replace platform/network boundaries with a
recording sender and a deliberately mismatched runtime bundle/plist fixture.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
analytics = (root / 'RoamControl/Services/UsageAnalyticsService.swift').read_text()
helper = (root / 'RoamControl/Services/BackgroundTaskIdentifier.swift').read_text()

def block(source, marker):
    start = source.index(marker)
    opening = source.index('{', start)
    depth = 0
    for i in range(opening, len(source)):
        if source[i] == '{': depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0: return source[start:i+1]
    raise AssertionError(marker)

fixture = '''
enum RuntimeFixture {
    static let bundleIdentifier: String? = "com.sean.roamcontrol.TESTSUFFIX"
    static func object(forInfoDictionaryKey: String) -> Any? {
        ["com.sean.roamcontrol.pairing.*", "com.sean.roamcontrol.location.*"]
    }
}
struct UIDevice { static let current = UIDevice(); let systemVersion = "27.0" }
'''
source = 'import Foundation\n' + fixture + helper
keep_alive = (root / 'RoamControl/Services/BackgroundLocationKeepAlive.swift').read_text()
source += keep_alive[keep_alive.index('struct BackgroundSessionTelemetry'):keep_alive.index('/// Receives')]
source += analytics[analytics.index('enum UsageAnalyticsEvent:'):analytics.index('/// Sends')]
source += analytics[analytics.index('struct FailureDiagnosticSnapshot'):]
source += analytics[analytics.index('private struct SelfHostedAnalyticsSignal'):analytics.index('private struct AnalyticsConfiguration')]
routing = analytics[analytics.index('        let diagnostic = failure?.0'):analytics.index('        guard let data = try? JSONEncoder().encode(payload)')]
source += '''
struct Destinations { let hasConfiguredDestination: Bool }
final class Recorder {
    static let destinations = Destinations(hasConfiguredDestination: true)
    var reportingEnabled = false
    var rows: [[String: Any]] = []
''' + block(analytics, '    func recordFailure(\n') + '''
    func send(_ event: UsageAnalyticsEvent, destinations: Destinations,
              failure: (FailureDiagnosticSnapshot, FailureContext)?) {
        let appVersion = "0.9.2"
        let buildNumber = "60"
        let background: BackgroundSessionTelemetry? = BackgroundSessionTelemetry(status: .receivingUpdates, started: true, schedulerAvailable: false)
        let clientIdentifier = "anonymous-test"
''' + routing + '''
        rows.append(try! JSONSerialization.jsonObject(with: JSONEncoder().encode(payload)) as! [String: Any])
    }
}
'''
for component, file in [('pairing','Pairing/OnDevicePairingCoordinator.swift'), ('location','Tunnel/LocalDeviceSessionCoordinator.swift')]:
    code = (root / 'RoamControl/Services' / file).read_text()
    phase = 'OnDevicePairingPhase' if component == 'pairing' else 'DeviceSessionPhase'
    source += f'enum {phase}: Equatable {{ case idle, preparing, connecting, failed(String) }}\n'
    source += f'final class {component.title()}Harness {{\n'
    source += block(code, '    private(set) var phase:') + '\n'
    source += '''
    var schedulerRegistrationAccepted = false
    var terminalFailureReported = false
    var lastFailureStage: FailureStage?
    var lastFailureDisposition: FailureDisposition?
    var schedulerFailureReason: SchedulerFailureReason?
    var taskConfigurationStatus: BackgroundTaskConfigurationStatus = .notChecked
    var taskRegistrationStatus: BackgroundTaskRegistrationStatus = .notAttempted
    var recordStore: Int? = 1
    var onRecoveryNeeded: ((FailureDiagnosticSnapshot) -> Void)?
    var onFailure: ((FailureDiagnosticSnapshot) -> Void)?
    var backgroundTelemetry = BackgroundSessionTelemetry(status: .idle, started: false, schedulerAvailable: false)
    var onBackgroundEvent: ((UsageAnalyticsEvent, BackgroundSessionTelemetry) -> Void)?
''' + f'    var onPhaseChange: (({phase}) -> Void)?\n'
    source += block(code, '    private func failureSnapshot(') + '\n'
    if component == 'location':
        source += block(code, '    private func reportSchedulerObservationFailure()') + '\n'
    start = code.index(f'        taskConfigurationStatus = BackgroundTaskIdentifier.configurationStatus(for: "{component}")')
    end = code.index('        let identifier =', start) if component == 'location' else code.index('        // Pairing must not depend', start)
    source += '    func preflight() {\n        phase = .preparing\n        terminalFailureReported = false\n' + code[start:end] + ('\n        _ = prefix\n' if component == 'location' else '\n') + '    }\n'
    source += '    func fail(_ message: String) { phase = .failed(message) }\n}\n'
    expected_count = 2 if component == 'location' else 0
    expected_event = 'RoamControl.Failure.Observed' if component == 'pairing' else 'RoamControl.Connection.RecoveryNeeded'
    expected_disposition = 'terminal' if component == 'pairing' else 'recoverable'
    callback = 'onFailure' if component == 'pairing' else 'onRecoveryNeeded'
    source += (f'''
do {{
    let coordinator = {component.title()}Harness()
    let recorder = Recorder()
    var captured: FailureDiagnosticSnapshot?
    coordinator.{callback} = {{ snapshot in
        captured = snapshot
        recorder.recordFailure(snapshot, context: .{component}, enabled: true)
    }}
    coordinator.preflight()
    precondition(recorder.rows.count == {expected_count})
    let row = recorder.rows[0]
    precondition(row["event_name"] as? String == "{expected_event}")
    precondition(row["failure_context"] as? String == "{component}")
    precondition(row["failure_stage"] as? String == "schedulerRegistration")
    precondition(row["failure_disposition"] as? String == "{expected_disposition}")
    precondition(row["{component}_task_configuration"] as? String == "Runtime identifier wildcard not permitted")
    precondition(row["{component}_task_registration"] as? String == "Not attempted")
    precondition(row["runtime_bundle_identifier"] as? String == RuntimeFixture.bundleIdentifier)
    precondition(row["permitted_background_tasks"] as? [String] == RuntimeFixture.object(forInfoDictionaryKey: "") as? [String])
    precondition(row["ios_version"] as? String == "27.0")
    precondition(row["scheduler_reason"] == nil)
    precondition(row["background_keep_alive"] as? String == "coreLocation")
    precondition(row["background_keep_alive_status"] as? String == "receivingUpdates")
    precondition(row["background_keep_alive_started"] as? Bool == true)
    precondition(row["bg_task_scheduler_available"] as? Bool == false)
    coordinator.taskConfigurationStatus = .permitted
    coordinator.taskRegistrationStatus = .accepted
    precondition(captured?.taskConfigurationStatus == .runtimeIdentifierNotPermitted)
    precondition(captured?.taskRegistrationStatus == .notAttempted)
}}
''' if component == 'location' else '')
source += '''
do {
    let recorder = Recorder()
    for disposition: FailureDisposition in [.terminal, .recoverable] {
        for stage: FailureStage in [.schedulerRegistration, .schedulerSubmission, .pairingEngine] {
            recorder.rows = []
            let snapshot = FailureDiagnosticSnapshot(stage: stage, disposition: disposition,
                schedulerReason: .notPermitted, taskConfigurationStatus: .permitted,
                taskRegistrationStatus: .accepted)
            recorder.recordFailure(snapshot, context: .location, enabled: false)
            precondition(recorder.rows.isEmpty)
            recorder.recordFailure(snapshot, context: .location, enabled: true)
            precondition(recorder.rows.count == (snapshot.isSchedulerFailure && disposition == .recoverable ? 2 : 1))
            if snapshot.isSchedulerFailure {
                precondition(recorder.rows.filter { $0["event_name"] as? String == "RoamControl.Failure.Observed" }.count == 1)
            } else {
                precondition(recorder.rows[0]["runtime_bundle_identifier"] == nil)
                precondition(recorder.rows[0]["permitted_background_tasks"] == nil)
                precondition(recorder.rows[0]["scheduler_reason"] == nil)
            }
        }
    }
    recorder.rows = []
    recorder.recordFailure(FailureDiagnosticSnapshot(stage: .schedulerRegistration,
        taskConfigurationStatus: .runtimeIdentifierNotPermitted, taskRegistrationStatus: .notAttempted),
        context: .restoration, enabled: true)
    precondition(recorder.rows[0]["location_task_registration"] as? String == "Not attempted")
    recorder.rows = []
    recorder.send(.pairingFailed, destinations: Recorder.destinations, failure: nil)
    precondition(recorder.rows[0]["event_name"] as? String == "RoamControl.Pairing.Failed")
    precondition(recorder.rows[0]["failure_stage"] == nil)
    precondition(recorder.rows[0]["runtime_bundle_identifier"] == nil)
}
print("Pairing/location preflight, immutable snapshot, scheduler event, privacy and JSON checks passed")
'''
source = source.replace('Bundle.main', 'RuntimeFixture')
with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / 'main.swift'
    path.write_text(source)
    binary = Path(temp) / 'check'
    subprocess.run(['xcrun','swiftc','-module-cache-path',str(Path(temp)/'cache'),str(path),'-o',str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
