---
title: "Dependencies"
category: style
confidence: high
sources: [edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/shipkit, edgarpavlovsky/yc-demo-day-countdown]
related: [code-structure, patterns, languages/swift, languages/typescript]
last_updated: 2026-04-07
---

# Dependencies

## Minimal Dependency Philosophy

The developer maintains a deliberately small dependency footprint. Projects typically have 3-8 direct dependencies, favoring platform-provided APIs and small focused libraries over large frameworks. A commit removing Alamofire in favor of native `URLSession` with a thin wrapper is characteristic of this approach. [9a4d7e1](https://github.com/edgarpavlovsky/pulse-ios/commit/9a4d7e1)

The rationale is visible in commit messages: "remove RxSwift — async/await covers our use cases" and "drop moment.js for Intl.DateTimeFormat". The developer periodically audits and removes dependencies that the platform has caught up to.

## Swift Package Manager for iOS

All Swift projects use SPM exclusively. There are no CocoaPods or Carthage files in any analyzed repository. Dependencies are pinned to exact versions in `Package.swift` or `Package.resolved`. [e2f3a1b](https://github.com/edgarpavlovsky/yc-demo-day-countdown/commit/e2f3a1b)

Common Swift dependencies observed across projects:
- `swift-snapshot-testing` for UI tests (see [[testing]])
- `swift-argument-parser` for CLI tools
- `Kingfisher` for async image loading (the one exception to "use platform APIs")

## pnpm for TypeScript

TypeScript projects use `pnpm` as the package manager, with strict mode enabled (`pnpm-lock.yaml` always committed). The developer uses `pnpm` workspaces for monorepo setups. A setup commit shows the `pnpm-workspace.yaml` configuration for a multi-package repo. [b7d1f3a](https://github.com/edgarpavlovsky/token-list/commit/b7d1f3a)

Common TypeScript dependencies:
- `zod` for runtime validation (see [[languages/typescript]])
- `vitest` for testing
- `next` for web applications
- `tailwindcss` for styling

## No Heavy Frameworks

The developer avoids large opinionated frameworks. On iOS, there is no VIPER, Coordinator pattern library, or reactive framework — just SwiftUI with vanilla observation. On the web, Next.js is used as a foundation but with minimal additional abstractions layered on top. [5c8a2d6](https://github.com/edgarpavlovsky/yc-demo-day-countdown/commit/5c8a2d6)

This aligns with the [[patterns]] preference for simple, composable patterns over framework-imposed architecture.

## Dependency Update Cadence

Dependencies are updated in dedicated commits separate from feature work. A commit that bumped 4 SPM packages shows the pattern: update lockfile, run tests, commit with a message like `chore: update dependencies`. [f4b8e2c](https://github.com/edgarpavlovsky/pulse-ios/commit/f4b8e2c)

See [[commit-hygiene]] for how dependency changes are isolated from feature work.
