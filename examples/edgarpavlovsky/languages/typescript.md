---
title: "TypeScript Idioms"
category: language
confidence: high
sources: [edgarpavlovsky/token-list, edgarpavlovsky/shipkit, edgarpavlovsky/gitstyle]
related: [patterns, type-discipline, testing, dependencies]
last_updated: 2026-04-07
---

# TypeScript Idioms

## Strict Mode Always

Every TypeScript project has `strict: true` in `tsconfig.json`, along with `noUncheckedIndexedAccess` and `noImplicitReturns`. The developer treats TypeScript compiler strictness as a feature, not a burden. [b7d1f3a](https://github.com/edgarpavlovsky/token-list/commit/b7d1f3a)

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## Zod for Runtime Validation

External data (API responses, user input, environment variables) is validated at the boundary using Zod schemas. The inferred types from Zod schemas serve as the canonical type definitions, avoiding the common problem of runtime data diverging from compile-time types. [c4f2e8b](https://github.com/edgarpavlovsky/token-list/commit/c4f2e8b)

```typescript
const TokenSchema = z.object({
    address: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
    symbol: z.string().min(1).max(11),
    decimals: z.number().int().min(0).max(18),
    chainId: z.number().int().positive(),
});

type Token = z.infer<typeof TokenSchema>;

// Used at API boundaries
const tokens = apiResponse.map((raw) => TokenSchema.parse(raw));
```

## Functional Patterns Over Classes

The developer prefers functions and closures over classes in TypeScript. State is managed through React hooks or simple module-level closures. When classes are used, they are rare and typically wrap a third-party SDK. [d8a3f1c](https://github.com/edgarpavlovsky/shipkit/commit/d8a3f1c)

```typescript
// Characteristic style — factory function, not a class
function createTokenCache(ttl: number) {
    const cache = new Map<string, { token: Token; expiresAt: number }>();

    return {
        get(address: string): Token | undefined {
            const entry = cache.get(address);
            if (!entry || entry.expiresAt < Date.now()) return undefined;
            return entry.token;
        },
        set(address: string, token: Token): void {
            cache.set(address, { token, expiresAt: Date.now() + ttl });
        },
    };
}
```

## Next.js with App Router

Web applications use Next.js with the App Router. The developer uses server components by default and only adds `"use client"` when interactivity is required. Data fetching happens in server components, with client components receiving data as props. [a2d6c4f](https://github.com/edgarpavlovsky/shipkit/commit/a2d6c4f)

```typescript
// app/tokens/page.tsx — server component
export default async function TokensPage() {
    const tokens = await fetchTokenList();
    return <TokenTable tokens={tokens} />;
}

// components/TokenTable.tsx — client component for interactivity
"use client";
export function TokenTable({ tokens }: { tokens: Token[] }) {
    const [filter, setFilter] = useState("");
    // ...
}
```

## Barrel Exports and Module Boundaries

Each feature directory has an `index.ts` that re-exports the public API. Internal implementation details are not exported, enforcing module boundaries at the file system level. [71bc9e3](https://github.com/edgarpavlovsky/token-list/commit/71bc9e3)

```typescript
// features/tokens/index.ts
export { TokenList } from "./TokenList";
export { useTokenSearch } from "./useTokenSearch";
export type { Token, TokenFilter } from "./types";
// Internal: TokenCache, tokenApi — not exported
```

See [[type-discipline]] for branded types and discriminated unions, and [[dependencies]] for the pnpm workspace setup.
