---
title: "Swift Idioms"
category: language
confidence: high
sources: [edgarpavlovsky/pulse-ios, edgarpavlovsky/yc-demo-day-countdown]
related: [patterns, type-discipline, testing, dependencies]
last_updated: 2026-04-07
---

# Swift Idioms

## SwiftUI as the Primary UI Framework

All iOS projects use SwiftUI exclusively — there is no UIKit code in any analyzed repository. Views are small and composable, typically under 80 lines. Complex views are broken into extracted subviews rather than growing a single body. [5c8a2d6](https://github.com/edgarpavlovsky/yc-demo-day-countdown/commit/5c8a2d6)

```swift
struct DashboardView: View {
    @State private var viewModel = DashboardViewModel()

    var body: some View {
        ScrollView {
            HeaderSection(profile: viewModel.profile)
            MetricsGrid(metrics: viewModel.weeklyMetrics)
            RecentActivityList(items: viewModel.recentItems)
        }
        .task { await viewModel.load() }
    }
}
```

The developer uses the `.task` modifier for async loading rather than `.onAppear` with a `Task` block, preferring the automatic cancellation behavior.

## Async/Await and Structured Concurrency

Swift concurrency is used throughout, with `async let` for parallel fetches and `TaskGroup` for dynamic concurrency. The developer avoids `DispatchQueue` in new code entirely. [9a4d7e1](https://github.com/edgarpavlovsky/pulse-ios/commit/9a4d7e1)

```swift
func refreshAll() async throws {
    async let profile = fetchProfile()
    async let settings = fetchSettings()
    async let notifications = fetchNotifications()

    self.state = .loaded(
        profile: try await profile,
        settings: try await settings,
        notifications: try await notifications
    )
}
```

## Result Type for Expected Failures

`Result<Success, Failure>` is used for domain errors where the caller is expected to handle specific failure cases. `throws` is reserved for unexpected errors that should propagate. See [[patterns]] for the broader error-handling philosophy. [4fb2c8d](https://github.com/edgarpavlovsky/pulse-ios/commit/4fb2c8d)

## Extensions for Organization

Extensions are used liberally to organize code within a file and to add functionality to standard library types. Each extension has a `// MARK:` comment and groups related methods. [4e8b2c7](https://github.com/edgarpavlovsky/pulse-ios/commit/4e8b2c7)

```swift
extension Date {
    var startOfDay: Date {
        Calendar.current.startOfDay(for: self)
    }

    func daysUntil(_ other: Date) -> Int {
        Calendar.current.dateComponents([.day], from: startOfDay, to: other.startOfDay).day ?? 0
    }
}
```

## Protocol-Oriented Design

Protocols define capabilities rather than hierarchies. The developer uses protocol extensions for default implementations and protocol composition for flexible type requirements. This enables the mock-based testing approach described in [[testing]]. [3da7f12](https://github.com/edgarpavlovsky/pulse-ios/commit/3da7f12)

```swift
protocol Persistable: Codable {
    static var storageKey: String { get }
}

extension Persistable {
    func save() throws {
        let data = try JSONEncoder().encode(self)
        UserDefaults.standard.set(data, forKey: Self.storageKey)
    }

    static func load() throws -> Self {
        guard let data = UserDefaults.standard.data(forKey: storageKey) else {
            throw StorageError.notFound
        }
        return try JSONDecoder().decode(Self.self, from: data)
    }
}
```

See [[type-discipline]] for how Swift's type system is leveraged beyond basic typing.
