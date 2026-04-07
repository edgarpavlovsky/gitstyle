---
title: "TypeScript Idioms"
category: language
confidence: high
sources: [anthropics/anthropic-sdk-typescript, anthropics/claude-code]
related: [naming-conventions, type-discipline, patterns, dependencies]
last_updated: 2026-04-07
---

# TypeScript Idioms

## Strict Mode Without Escape Hatches

The TypeScript SDK ships with `strict: true` in `tsconfig.json` and treats `// @ts-ignore`, `// @ts-expect-error`, and `as any` as code review red flags. The codebase compiles cleanly under strict mode without suppressions. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": false,
    "target": "ES2020",
    "module": "commonjs",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "dist"
  }
}
```

The `noUncheckedIndexedAccess` flag forces index access on arrays and records to return `T | undefined`, requiring explicit null checks. This catches a common class of runtime errors at compile time. This strictness is a Stainless default — the same tsconfig pattern appears in OpenAI's TypeScript SDK.

## Async Iterables for Streaming

Streaming uses async iterables (`for await...of`), the native JavaScript pattern for consuming async sequences. The `MessageStream` class implements `Symbol.asyncIterator`. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

```typescript
const stream = client.messages.stream({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Tell me a story" }],
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}
```

The stream also exposes `stream.on("text", callback)` for event-based consumption and `await stream.finalMessage()` for collecting the full response. Both patterns are fully typed. The convenience methods are hand-written on top of Stainless's generated streaming infrastructure.

## Discriminated Union Types

Content blocks, stream events, and error responses use discriminated unions with `type` as the discriminant. TypeScript verifies exhaustive handling at compile time. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

```typescript
type ContentBlock = TextBlock | ToolUseBlock;

interface TextBlock {
  type: "text";
  text: string;
}

interface ToolUseBlock {
  type: "tool_use";
  id: string;
  name: string;
  input: Record<string, unknown>;
}

function handleBlock(block: ContentBlock): string {
  switch (block.type) {
    case "text":
      return block.text;
    case "tool_use":
      return `Tool: ${block.name}`;
  }
}
```

Adding a new variant to `ContentBlock` without handling it in existing switches produces a compile error. This pattern is used throughout the SDK for any polymorphic API type.

## Interface Mirroring the Python SDK

The TypeScript SDK's public API mirrors the Python SDK as closely as language differences allow. Resource hierarchies, method semantics, and type structures are kept in sync. The differences are only where TypeScript conventions demand: camelCase method names, kebab-case filenames, `Promise<T>` return types. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

```typescript
const client = new Anthropic();
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
});
```

This cross-language parity — a direct consequence of both SDKs being generated from the same Stainless API spec — means documentation examples transliterate between languages with minimal changes. See [[code-structure]] for how directory layouts are kept parallel.

## `Record<string, unknown>` Over `any`

Where untyped data is unavoidable (e.g., tool use `input` payloads), the SDK uses `Record<string, unknown>` rather than `any`. This forces consumers to narrow before using the data. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

```typescript
interface ToolUseBlock {
  type: "tool_use";
  id: string;
  name: string;
  input: Record<string, unknown>; // not `any`
}

// consumer must narrow
const location = toolUse.input["location"];
if (typeof location === "string") {
  // now safe to use as string
}
```

## ESM and CJS Dual Publishing

The SDK publishes both ESM and CommonJS builds via `exports` with conditional `import` and `require` paths. This ensures compatibility across Node.js, bundlers (webpack, esbuild, rollup), and edge runtimes (Cloudflare Workers, Deno). [e9a3d56](https://github.com/anthropics/anthropic-sdk-typescript/commit/e9a3d56)

```json
{
  "exports": {
    ".": {
      "import": "./dist/esm/index.js",
      "require": "./dist/cjs/index.js",
      "types": "./dist/types/index.d.ts"
    }
  }
}
```

## Error Classes Extend `Error` Properly

All error classes extend `Error` with `Object.setPrototypeOf(this, ClassName.prototype)` — the pattern necessary in TypeScript when extending built-in classes. Without this, `instanceof` checks silently fail. [c9b4d15](https://github.com/anthropics/anthropic-sdk-typescript/commit/c9b4d15)

```typescript
export class APIError extends Error {
  readonly status: number | undefined;
  readonly headers: Headers | undefined;

  constructor(status: number | undefined, message: string | undefined, headers: Headers | undefined) {
    super(message);
    Object.setPrototypeOf(this, APIError.prototype);
    this.status = status;
    this.headers = headers;
  }
}
```

This is a known TypeScript footgun that Anthropic (and all Stainless-generated SDKs) handle correctly across every error subclass.

## Branded Types for IDs

Internal types use branded types (nominal typing via intersection with a unique symbol) to prevent mixing different ID types — a message ID cannot be accidentally used where a content block ID is expected. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

```typescript
type MessageId = string & { readonly __brand: "MessageId" };
type ContentBlockId = string & { readonly __brand: "ContentBlockId" };
```

At runtime these are plain strings. The branding prevents accidental interchange at compile time without runtime overhead.

## `readonly` by Default on Response Types

Response interfaces use `readonly` on all properties, signaling that response objects are immutable data. This aligns with the Python SDK's Pydantic `BaseModel` (similarly immutable by convention). [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

```typescript
interface Message {
  readonly id: string;
  readonly type: "message";
  readonly role: "assistant";
  readonly content: readonly ContentBlock[];
  readonly model: string;
  readonly stop_reason: StopReason | null;
  readonly usage: Usage;
}
```
