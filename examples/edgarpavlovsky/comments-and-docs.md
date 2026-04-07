---
title: "Comments & Documentation"
category: style
confidence: medium
sources: [edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/shipkit, edgarpavlovsky/yc-demo-day-countdown]
related: [naming-conventions, code-structure, testing]
last_updated: 2026-04-07
---

# Comments & Documentation

## Minimal Inline Comments

The developer writes very few inline comments. Code is expected to be self-documenting through descriptive [[naming-conventions]] and small, focused functions. When inline comments do appear, they explain *why* something is done, never *what*. [8f3b1a7](https://github.com/edgarpavlovsky/pulse-ios/commit/8f3b1a7)

```swift
// Delay needed because the animation system hasn't laid out the view yet
DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
    self.scrollToBottom()
}
```

A commit that removed 23 comments from a single file replaced them with better variable names and extracted helper functions, demonstrating a preference for code clarity over commentary. [f1a9c3d](https://github.com/edgarpavlovsky/pulse-ios/commit/f1a9c3d)

## Doc Comments on Public APIs

Public protocols, types, and functions consistently have `///` doc comments in Swift and `/** */` JSDoc comments in TypeScript. The doc comments focus on the contract — what a caller needs to know — rather than implementation details. [c7e2d1a](https://github.com/edgarpavlovsky/token-list/commit/c7e2d1a)

```swift
/// Validates a token address against the on-chain registry.
/// - Parameter address: A hex-encoded Ethereum address, including the `0x` prefix.
/// - Returns: The validated `Token` if the address is registered, or a failure
///   describing why validation failed.
/// - Note: Requires network access. Use `cachedToken(for:)` for offline lookups.
func validateToken(_ address: String) async -> Result<Token, TokenError>
```

## README as the Only Prose Doc

Each project has a `README.md` at the root and nothing else in terms of prose documentation. There are no `docs/` directories or wiki pages maintained alongside code. The README is concise — typically install instructions, one usage example, and environment variable requirements. [a9e1b0c](https://github.com/edgarpavlovsky/shipkit/commit/a9e1b0c)

## MARK Comments for Navigation

In Swift files, `// MARK: -` comments are used to create Xcode navigation landmarks. These appear at section boundaries within a file (e.g., lifecycle, public API, private helpers) but never as explanatory prose. [4e8b2c7](https://github.com/edgarpavlovsky/pulse-ios/commit/4e8b2c7)

```swift
// MARK: - Lifecycle
// MARK: - Public API
// MARK: - Private Helpers
```

## TODOs Are Rare and Tracked

`TODO` comments are uncommon. When they appear, they reference a specific issue or next step rather than serving as open-ended reminders. A search across all analyzed repos found only 4 TODO comments, each linked to a GitHub issue number. [d3f1a9b](https://github.com/edgarpavlovsky/shipkit/commit/d3f1a9b)

See [[commit-hygiene]] for how documentation changes are committed separately from code changes.
