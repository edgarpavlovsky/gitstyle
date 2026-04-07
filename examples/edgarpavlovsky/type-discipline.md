---
title: "Type Discipline"
category: style
confidence: high
sources: [edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/shipkit, edgarpavlovsky/yc-demo-day-countdown]
related: [patterns, naming-conventions, languages/swift, languages/typescript]
last_updated: 2026-04-07
---

# Type Discipline

## Strong Typing as Documentation

The developer treats the type system as the primary form of documentation. Types encode business rules and constraints, not just data shapes. A commit adding token validation replaced string comparisons with a `ChainId` enum, making invalid chain IDs unrepresentable at compile time. [b7d1f3a](https://github.com/edgarpavlovsky/token-list/commit/b7d1f3a)

## Codable Protocols in Swift

All network response models conform to `Codable` with explicit `CodingKeys` when API field names differ from Swift conventions. The developer uses custom `init(from:)` decoders for non-trivial mappings rather than stringly-typed workarounds. [6e9c4a2](https://github.com/edgarpavlovsky/pulse-ios/commit/6e9c4a2)

```swift
struct UserProfile: Codable {
    let id: UUID
    let displayName: String
    let joinedAt: Date
    let subscriptionTier: SubscriptionTier

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
        case joinedAt = "joined_at"
        case subscriptionTier = "subscription_tier"
    }
}
```

A commit fixing a date-parsing crash introduced a custom `JSONDecoder` with `.iso8601` date strategy, applied project-wide through a shared `APIClient`. [a1b7d3e](https://github.com/edgarpavlovsky/pulse-ios/commit/a1b7d3e)

## Branded Types in TypeScript

In TypeScript projects, the developer uses branded types to prevent mixing semantically different values that share the same primitive type. This pattern appears in the token-list project where wallet addresses and contract addresses are both strings but must not be interchanged. [c4f2e8b](https://github.com/edgarpavlovsky/token-list/commit/c4f2e8b)

```typescript
type WalletAddress = string & { readonly __brand: "WalletAddress" };
type ContractAddress = string & { readonly __brand: "ContractAddress" };

function transfer(from: WalletAddress, to: ContractAddress, amount: bigint): Promise<TxHash> {
    // Type system prevents accidentally swapping from/to
}
```

## Discriminated Unions for State

Complex state is always modeled as discriminated unions rather than optional fields or boolean flags. See [[patterns]] for how this integrates with error handling. [d8a3f1c](https://github.com/edgarpavlovsky/shipkit/commit/d8a3f1c)

```typescript
type DeployState =
    | { status: "idle" }
    | { status: "building"; progress: number }
    | { status: "deploying"; buildId: string }
    | { status: "live"; url: string; deployedAt: Date }
    | { status: "failed"; error: string; buildId: string };
```

## Avoiding `any` and Force-Unwrapping

In TypeScript, `any` is effectively banned — `unknown` is used when the type is genuinely uncertain, followed by runtime narrowing. The tsconfig enforces `strict: true` and `noImplicitAny`. In Swift, force-unwrapping (`!`) does not appear in production code. Optionals are handled through `guard let`, `if let`, or nil-coalescing. [a4c2e8f](https://github.com/edgarpavlovsky/yc-demo-day-countdown/commit/a4c2e8f)

See [[languages/swift]] and [[languages/typescript]] for language-specific type system usage.
