import Foundation

enum BackgroundTaskConfigurationStatus: String {
    case notChecked = "Not checked"
    case permitted = "Permitted identifier matched"
    case missingPermittedIdentifiers = "Permitted identifier list missing"
    case identifierNotPermitted = "Generated identifier not permitted"
}

enum BackgroundTaskRegistrationStatus: String {
    case notAttempted = "Not attempted"
    case accepted = "Accepted"
    case rejected = "Rejected"
}

enum BackgroundTaskIdentifier {
    static func prefix(for component: String) -> String {
        let wildcardSuffix = ".\(component).*"
        let bundleIdentifier = Bundle.main.bundleIdentifier ?? "com.sean.roamcontrol"

        if let permittedIdentifiers = Bundle.main.object(
            forInfoDictionaryKey: "BGTaskSchedulerPermittedIdentifiers"
        ) as? [String] {
            let matchingIdentifier = permittedIdentifiers.first(where: {
                $0.hasPrefix("\(bundleIdentifier).") && $0.hasSuffix(wildcardSuffix)
            })
            let fallbackIdentifier = permittedIdentifiers.first(where: {
                $0.hasSuffix(wildcardSuffix)
            })

            if let wildcardIdentifier = matchingIdentifier ?? fallbackIdentifier {
                return String(wildcardIdentifier.dropLast(2))
            }
        }

        return "\(bundleIdentifier).\(component)"
    }

    static func configurationStatus(for identifier: String) -> BackgroundTaskConfigurationStatus {
        guard
            let permittedIdentifiers = Bundle.main.object(
                forInfoDictionaryKey: "BGTaskSchedulerPermittedIdentifiers"
            ) as? [String],
            !permittedIdentifiers.isEmpty
        else { return .missingPermittedIdentifiers }

        let isPermitted = permittedIdentifiers.contains { permittedIdentifier in
            guard permittedIdentifier.hasSuffix(".*") else {
                return permittedIdentifier == identifier
            }

            let prefix = String(permittedIdentifier.dropLast())
            return identifier.hasPrefix(prefix) && identifier.count > prefix.count
        }

        return isPermitted ? .permitted : .identifierNotPermitted
    }
}
