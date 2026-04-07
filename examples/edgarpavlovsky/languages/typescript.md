---
title: "TypeScript Idioms"
category: language
confidence: medium
sources: [edgarpavlovsky/token-list]
related: [naming-conventions, patterns, type-discipline]
last_updated: 2026-04-07
---

# TypeScript Idioms

## Type Usage

TypeScript strict mode is the default. The developer uses the type system actively to catch errors at compile time rather than runtime. See [[type-discipline]] for cross-language typing patterns.

```typescript
// Interfaces for data shapes
interface TokenInfo {
  address: string;
  chainId: number;
  symbol: string;
  decimals: number;
  name: string;
  logoURI?: string;
}

// Strict function signatures
function getToken(address: string, chainId: number): TokenInfo | undefined {
  return tokenList.find(t => t.address === address && t.chainId === chainId);
}
```

## Module System

ES module syntax (`import`/`export`) used exclusively. CommonJS (`require`) is not used in TypeScript projects. [b7d1f3a](https://github.com/edgarpavlovsky/token-list/commit/b7d1f3a)

## Async Patterns

`async/await` is the standard pattern. Promise chains with `.then()` are avoided. Error handling uses `try/catch` at the call site.

## Utility Types

The developer uses TypeScript's built-in utility types (`Partial<T>`, `Pick<T>`, `Omit<T>`, `Record<K,V>`) rather than defining equivalent custom types.

## Configuration

`tsconfig.json` uses strict mode with standard settings. Path aliases are used sparingly — typically only for deep imports in larger projects.
