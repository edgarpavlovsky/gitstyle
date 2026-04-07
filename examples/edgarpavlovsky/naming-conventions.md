---
title: "Naming Conventions"
category: style
confidence: high
sources: [edgarpavlovsky/yc-demo-day-countdown, edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/shipkit]
related: [code-structure, comments-and-docs, type-discipline]
last_updated: 2026-04-07
---

# Naming Conventions

## Language-Idiomatic Casing

The developer follows platform conventions strictly, never mixing styles across language boundaries:

- **Swift**: `camelCase` for variables and functions, `PascalCase` for types, protocols, and enums. [a4c2e8f](https://github.com/edgarpavlovsky/yc-demo-day-countdown/commit/a4c2e8f)
- **TypeScript**: `camelCase` for variables and functions, `PascalCase` for types, interfaces, and React components. [b7d1f3a](https://github.com/edgarpavlovsky/token-list/commit/b7d1f3a)

Constants use `SCREAMING_SNAKE_CASE` in TypeScript but remain `camelCase` in Swift, following each ecosystem's norms. A commit that introduced shared constants across both codebases shows this distinction clearly. [d42ea91](https://github.com/edgarpavlovsky/shipkit/commit/d42ea91)

## Descriptive, Self-Documenting Names

Names are descriptive but not verbose. The developer avoids single-letter variables except for conventional iterators (`i`, `j`) and Swift closures (`$0`). There is a strong preference for names that eliminate the need for comments:

```swift
// Characteristic style
let countdownTimer = Timer.scheduledTimer(...)
let daysRemaining = calculateDays(until: targetDate)
let isSubscriptionActive = subscription.expiresAt > Date.now

// Not typical — too terse
let t = Timer.scheduledTimer(...)
let d = calculateDays(until: td)
```

A rename-heavy commit changed `proc` to `processPayment`, `cfg` to `appConfiguration`, and `mgr` to `sessionManager` across 14 files. [8f3b1a7](https://github.com/edgarpavlovsky/pulse-ios/commit/8f3b1a7)

## Verb-First for Actions, Nouns for Data

Functions that perform side effects start with a verb. Computed properties and pure functions that return values use noun phrases:

```typescript
// Actions — verb-first
function fetchTokenList(): Promise<Token[]>
function validateAddress(addr: string): boolean
function syncWalletBalances(): Promise<void>

// Data — noun phrases
function totalSupply(): bigint
function formattedCountdown(to date: Date): string
```

This pattern is consistent across 90%+ of observed functions. [c5e7d2a](https://github.com/edgarpavlovsky/token-list/commit/c5e7d2a)

## Boolean Naming

Booleans consistently use `is`, `has`, or `should` prefixes. A commit that added feature flags shows all five flags following this pattern: `isOnboardingComplete`, `hasActiveSubscription`, `shouldShowPaywall`, `isDebugMode`, `hasCompletedTutorial`. [2ca8f6e](https://github.com/edgarpavlovsky/pulse-ios/commit/2ca8f6e)

## File and Branch Naming

Files are named after their primary export:
- Swift: `PascalCase.swift` (e.g., `CountdownView.swift`, `TokenValidator.swift`)
- TypeScript: `camelCase.ts` for utilities, `PascalCase.tsx` for React components

Branch names follow `type/short-description` format — see [[commit-hygiene]] for details.
