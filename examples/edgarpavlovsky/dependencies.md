---
title: "Dependencies"
category: style
confidence: medium
sources: [edgarpavlovsky/yc-demo-day-countdown, edgarpavlovsky/token-list]
related: [patterns, code-structure]
last_updated: 2026-04-07
---

# Dependencies

## Philosophy

The developer takes a minimalist approach to dependencies. Projects tend to use platform-native APIs and first-party frameworks over third-party libraries. When external dependencies are used, they're well-established, widely-adopted packages rather than niche or experimental ones.

## Swift

- **UI**: SwiftUI (first-party) rather than third-party UI frameworks
- **Networking**: `URLSession` (Foundation) rather than Alamofire
- **Data**: Native `Codable` for serialization
- **Package manager**: Swift Package Manager (SPM)

## TypeScript / JavaScript

- **Build tools**: Standard toolchains (TypeScript compiler, standard bundlers)
- **Package manager**: npm
- **Libraries**: Prefers well-known, minimal dependencies

## Build Tools

Projects use the standard build tools for each ecosystem without complex custom build pipelines. Configuration is kept minimal and conventional.

## Dependency Updates

No strong evidence of automated dependency update tooling (like Dependabot) in public repos, though this may differ in private repositories.
