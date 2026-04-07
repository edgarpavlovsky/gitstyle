---
title: "Code Structure"
category: style
confidence: high
sources: [edgarpavlovsky/yc-demo-day-countdown, edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/shipkit]
related: [naming-conventions, patterns, dependencies]
last_updated: 2026-04-07
---

# Code Structure

## Feature-Based Folder Organization

Projects consistently use a feature-based directory layout rather than grouping by file type. Each feature gets its own folder containing views, models, and services together. This pattern appears across both Swift and TypeScript codebases. [e2f3a1b](https://github.com/edgarpavlovsky/pulse-ios/commit/e2f3a1b)

```
Features/
  Dashboard/
    DashboardView.swift
    DashboardViewModel.swift
    DashboardService.swift
  Settings/
    SettingsView.swift
    SettingsStore.swift
```

This was reinforced in a later refactor that moved shared networking code out of a feature folder and into a top-level `Services/` directory, keeping the feature folders focused on domain logic. [f8a42cd](https://github.com/edgarpavlovsky/pulse-ios/commit/f8a42cd)

## Small, Focused Modules

Files rarely exceed 150-200 lines. When a file grows beyond that threshold, it gets decomposed along responsibility boundaries. A characteristic commit split a 340-line `TokenListManager` into three files: `TokenFetcher`, `TokenValidator`, and `TokenCache`. [71bc9e3](https://github.com/edgarpavlovsky/token-list/commit/71bc9e3)

The same principle applies to TypeScript — utility modules are broken into single-responsibility files rather than growing a monolithic `utils.ts`. See [[naming-conventions]] for how files are named after their primary export.

## UI / Domain / Data Layer Separation

There is a clear three-layer architecture across iOS projects:

1. **UI Layer** — SwiftUI views and view models, no direct network calls
2. **Domain Layer** — Business logic, protocols, and model transformations
3. **Data Layer** — Network clients, persistence, third-party SDK wrappers

A commit introducing a new onboarding flow demonstrates this: the view only talks to a `OnboardingCoordinator` protocol, which is backed by a concrete implementation that calls the data layer. [3da7f12](https://github.com/edgarpavlovsky/pulse-ios/commit/3da7f12)

This mirrors the [[patterns]] preference for dependency injection — layers communicate through protocols, never concrete types.

## Entry Points and Configuration

- Entry points are always clearly named (`App.swift`, `index.ts`, `main.ts`)
- Configuration lives at the project root (`tsconfig.json`, `.env`, `Package.swift`)
- Test files mirror the source tree structure (see [[testing]])
- Static assets live in dedicated directories (`Assets/`, `public/`)

A repo setup commit shows the full skeleton with these conventions already in place, suggesting this is a deliberate template the developer starts from. [a9e1b0c](https://github.com/edgarpavlovsky/shipkit/commit/a9e1b0c)

## Monorepo Tendencies

The TypeScript projects use a lightweight monorepo pattern with `pnpm` workspaces. Packages are split into `packages/core`, `packages/ui`, and `apps/web`, keeping shared logic in one place without heavy tooling. See [[dependencies]] for package manager preferences.
