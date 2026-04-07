---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/yc-demo-day-countdown, edgarpavlovsky/shipkit]
related: [code-structure, type-discipline, dependencies, testing]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Async/Await Over Callbacks

The developer exclusively uses `async/await` for asynchronous code. In Swift, this means structured concurrency with `Task` groups and async sequences. In TypeScript, all async functions use `await` rather than `.then()` chains. [c1d4e5f](https://github.com/edgarpavlovsky/token-list/commit/c1d4e5f)

```swift
func fetchDashboardData() async throws -> DashboardState {
    async let profile = profileService.fetchCurrent()
    async let metrics = metricsService.fetchWeekly()
    async let notifications = notificationService.fetchUnread()

    return DashboardState(
        profile: try await profile,
        metrics: try await metrics,
        notifications: try await notifications
    )
}
```

A refactor commit converted 12 completion-handler-based methods to `async/await` in a single pass, reducing the networking layer by ~80 lines. [9a4d7e1](https://github.com/edgarpavlovsky/pulse-ios/commit/9a4d7e1)

## Result Types for Error Handling

The developer prefers `Result<Success, Failure>` in Swift for operations that can fail in expected ways, reserving `throws` for truly exceptional cases. In TypeScript, a similar pattern uses discriminated unions (see [[type-discipline]]). [4fb2c8d](https://github.com/edgarpavlovsky/pulse-ios/commit/4fb2c8d)

```swift
enum TokenError: Error {
    case invalidAddress
    case networkUnavailable
    case rateLimited(retryAfter: TimeInterval)
}

func validateToken(_ address: String) -> Result<Token, TokenError> {
    guard address.hasPrefix("0x") else {
        return .failure(.invalidAddress)
    }
    // ...
}
```

## Dependency Injection via Protocols

Services are defined as protocols and injected through initializers. This supports testability (see [[testing]]) and keeps modules decoupled. The developer avoids service locator patterns or singletons. [3da7f12](https://github.com/edgarpavlovsky/pulse-ios/commit/3da7f12)

```swift
protocol AnalyticsService {
    func track(_ event: AnalyticsEvent)
}

class OnboardingViewModel: ObservableObject {
    private let analytics: AnalyticsService

    init(analytics: AnalyticsService = LiveAnalyticsService()) {
        self.analytics = analytics
    }
}
```

A commit introducing a test suite for the onboarding flow shows `MockAnalyticsService` being injected in its place, confirming this is a deliberate testability pattern. [e71f3b9](https://github.com/edgarpavlovsky/pulse-ios/commit/e71f3b9)

## Observer Pattern for Reactivity

SwiftUI projects use `@Observable` (or `ObservableObject` in older commits) as the primary reactivity mechanism. State changes flow downward through the view hierarchy, and user actions flow upward through closures or method calls. The developer avoids Combine publishers for new code, preferring the native observation framework. [5c8a2d6](https://github.com/edgarpavlovsky/yc-demo-day-countdown/commit/5c8a2d6)

In TypeScript, the equivalent pattern uses React's `useState`/`useReducer` with context providers for shared state, avoiding external state management libraries entirely. See [[dependencies]] for the minimal-deps philosophy.

## Guard-Early, Return-Early

Functions validate preconditions at the top with `guard` statements (Swift) or early returns (TypeScript) before proceeding to the main logic. This keeps the "happy path" at the lowest indentation level and avoids deep nesting.
