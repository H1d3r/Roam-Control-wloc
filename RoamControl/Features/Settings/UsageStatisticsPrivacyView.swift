import SwiftUI

struct UsageStatisticsPrivacyView: View {
    var body: some View {
        List {
            Section {
                Label {
                    Text("Roam Control sends only a small, fixed set of anonymous activity counts when sharing is enabled.")
                } icon: {
                    Image(systemName: "checkmark.shield.fill")
                        .foregroundStyle(.green)
                }
            }

            Section("Shared") {
                privacyRow("Hashed random installation identifier", symbol: "number.circle")
                privacyRow("Approximate event time", symbol: "clock")
                privacyRow("App opened or returned to foreground", symbol: "app.badge.checkmark")
                privacyRow("App version and build", symbol: "number")
                privacyRow("Introduction completed", symbol: "sparkles")
                privacyRow("Connection help, retry and retry success counts", symbol: "arrow.clockwise")
                privacyRow("Fixed failure stage, scheduler reason, operation and recovery category", symbol: "exclamationmark.triangle")
                privacyRow("Fixed pairing and location task configuration and registration states on scheduler failures", symbol: "gearshape.2")
                privacyRow("Background session support, permission status and scheduler availability", symbol: "location.circle")
                privacyRow("iOS version (maintainer service only)", symbol: "iphone")
                privacyRow("Installed app and permitted background-task identifiers on scheduler failures (maintainer service only)", symbol: "gearshape")
                privacyRow("Pairing completed", symbol: "iphone.and.arrow.forward")
                privacyRow("Fixed or walking session started", symbol: "figure.walk")
                privacyRow("Active location updated", symbol: "location.fill")
            }

            Section("Never Shared") {
                privacyRow("Coordinates or place names", symbol: "mappin.slash")
                privacyRow("Searches, favourites, history or routes", symbol: "magnifyingglass")
                privacyRow("Pairing records or PINs", symbol: "key.slash")
                privacyRow("Apple ID, device name or personal details", symbol: "person.crop.circle.badge.xmark")
                privacyRow("Raw error messages or credentials", symbol: "lock.shield")
                privacyRow("Full diagnostic reports", symbol: "doc.text.magnifyingglass")
            }

            Section("Storage and Control") {
                Text("A random identifier is created for this installation and irreversibly hashed before it is sent. It is used only to estimate activity from participating installations.")
                    .foregroundStyle(.secondary)

                Text("Turning sharing off stops new reporting, cancels requests still in progress where possible and removes the identifier from Roam Control. It cannot withdraw anonymous events already received.")
                    .foregroundStyle(.secondary)

                Text("Events are sent to Roam Control's maintainer-operated service and, in configured beta builds, TelemetryDeck. The self-hosted service receives ordinary HTTPS connection metadata, such as the source IP address, but the app does not include it in the event body.")
                    .foregroundStyle(.secondary)

                Text("The self-hosted service runs daily maintenance that deletes live events older than 90 days. No fixed deletion schedule is promised for database backups or web-server access logs. TelemetryDeck says it does not store IP addresses and may retain anonymous events for roughly 7–10 years without guaranteeing an exact deletion date.")
                    .foregroundStyle(.secondary)

                Text("Roam Control uses a narrow first-party sender instead of an analytics SDK, so extra device metadata is not added automatically.")
                    .foregroundStyle(.secondary)
            }
        }
        .navigationTitle("Anonymous Statistics")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func privacyRow(_ title: String, symbol: String) -> some View {
        Label(title, systemImage: symbol)
    }
}

#Preview {
    NavigationStack {
        UsageStatisticsPrivacyView()
    }
}
