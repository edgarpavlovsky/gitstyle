---
title: "Testing"
category: style
confidence: medium
sources: [edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/shipkit]
related: [patterns, code-structure, type-discipline]
last_updated: 2026-04-07
---

# Testing

## Unit Tests for Business Logic

The developer writes unit tests primarily for business logic and data transformations. View-level code is tested less frequently, with the expectation that the type system and SwiftUI previews catch UI issues. Test coverage is concentrated where bugs would be most costly. [e71f3b9](https://github.com/edgarpavlovsky/pulse-ios/commit/e71f3b9)

```swift
func testCountdownCalculation() {
    let target = Date(timeIntervalSince1970: 1700000000)
    let now = Date(timeIntervalSince1970: 1699900000)
    let result = CountdownCalculator.daysRemaining(from: now, to: target)
    XCTAssertEqual(result, 1)
}
```

Test files live alongside source files in a mirrored directory structure (see [[code-structure]]), making it easy to find the tests for any given module.

## Snapshot Tests for UI Components

SwiftUI views that have complex conditional rendering get snapshot tests. The developer uses a lightweight snapshot testing approach that captures rendered view hierarchies and compares against reference images. [2f8a4c1](https://github.com/edgarpavlovsky/pulse-ios/commit/2f8a4c1)

```swift
func testDashboardEmptyState() {
    let view = DashboardView(viewModel: .mock(state: .empty))
    assertSnapshot(matching: view, as: .image(layout: .device(config: .iPhone13)))
}

func testDashboardLoadedState() {
    let view = DashboardView(viewModel: .mock(state: .loaded(sampleData)))
    assertSnapshot(matching: view, as: .image(layout: .device(config: .iPhone13)))
}
```

## Mock Protocols for Dependency Injection

Every service protocol has a corresponding mock implementation used exclusively in tests. Mocks are minimal — they record calls and return preconfigured values rather than reimplementing logic. This directly leverages the [[patterns]] approach to dependency injection. [b3c9d7e](https://github.com/edgarpavlovsky/pulse-ios/commit/b3c9d7e)

```swift
class MockAnalyticsService: AnalyticsService {
    var trackedEvents: [AnalyticsEvent] = []

    func track(_ event: AnalyticsEvent) {
        trackedEvents.append(event)
    }
}
```

## Focused Test Helpers

Rather than building a large shared test utilities library, the developer creates small, focused helpers scoped to individual test files or feature test suites. A common pattern is a `.mock(...)` static factory on model types that provides sensible defaults. [7d1e5f3](https://github.com/edgarpavlovsky/pulse-ios/commit/7d1e5f3)

```swift
extension UserProfile {
    static func mock(
        name: String = "Test User",
        tier: SubscriptionTier = .free
    ) -> UserProfile {
        UserProfile(id: UUID(), displayName: name, joinedAt: .now, subscriptionTier: tier)
    }
}
```

## TypeScript Testing

In TypeScript projects, tests use Vitest with a similar philosophy: focused unit tests for logic, minimal mocking, and type-safe test fixtures. Integration tests hit a local dev server rather than mocking HTTP calls. [a2d6c4f](https://github.com/edgarpavlovsky/token-list/commit/a2d6c4f)

See [[languages/swift]] and [[languages/typescript]] for language-specific testing patterns.
