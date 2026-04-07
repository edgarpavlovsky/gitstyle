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

The TypeScript SDK ships with `strict: true` in `tsconfig.json` and treats any `// @ts-ignore`, `// @ts-expect-error`, or `as any` as a code review red flag. The codebase compiles cleanly under strict mode — no suppressions needed. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

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

The `noUncheckedIndexedAccess` flag is enabled, meaning index access on arrays and records returns `T | undefined`, forcing explicit null checks. This catches a common class of runtime errors at compile time.

## Async Iterables for Streaming

Streaming in the TypeScript SDK uses async iterables (`for await...of`), the native JavaScript pattern for consuming async sequences. The `MessageStream` class implements `Symbol.asyncIterator`, making it usable with `for await`. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

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

The stream also exposes convenience methods: `stream.on("text", callback)` for event-based consumption and `await stream.finalMessage()` for collecting the full response. Both patterns are fully typed.

## Discriminated Union Types

Content blocks, stream events, and error responses use TypeScript discriminated unions with the `type` field as discriminant. This enables exhaustive narrowing with `switch` statements that TypeScript can verify at compile time. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

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

// exhaustive narrowing
function handleBlock(block: ContentBlock): string {
  switch (block.type) {
    case "text":
      return block.text; // TypeScript knows block is TextBlock
    case "tool_use":
      return `Tool: ${block.name}`; // TypeScript knows block is ToolUseBlock
  }
}
```

The `switch` is exhaustive — adding a new variant to `ContentBlock` without handling it in existing switches produces a compile error. This pattern is used throughout the SDK for any polymorphic API type.

## Interface Mirroring the Python SDK

The TypeScript SDK's public API mirrors the Python SDK as closely as language differences allow. Method names, parameter structures, and resource hierarchies are kept in sync. The differences are only where TypeScript conventions demand it: camelCase method names, kebab-case filenames, `Promise<T>` return types. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

```typescript
// TypeScript — mirrors Python SDK structure
const client = new Anthropic();
const message = await client.messages.create({
  model: "claude-sonnet-4-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello" }],
});
```

This cross-language parity means documentation examples can be "transliterated" between languages with minimal changes. See [[code-structure]] for how the directory layouts are kept in parallel.

## `Record<string, unknown>` Over `any`

Where untyped data is unavoidable (e.g., tool use `input` payloads), the SDK uses `Record<string, unknown>` rather than `any`. This forces consumers to narrow the type before using the data, preventing silent type errors. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

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

The TypeScript SDK publishes both ESM and CommonJS builds. The `package.json` uses `exports` with conditional `import` and `require` paths. This ensures compatibility across Node.js, bundlers (webpack, esbuild, rollup), and edge runtimes (Cloudflare Workers, Deno). [e9a3d56](https://github.com/anthropics/anthropic-sdk-typescript/commit/e9a3d56)

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

All error classes extend `Error` with proper prototype chain restoration — the `Object.setPrototypeOf(this, ClassName.prototype)` pattern that is necessary in TypeScript when extending built-in classes. This ensures `instanceof` checks work correctly. [c9b4d15](https://github.com/anthropics/anthropic-sdk-typescript/commit/c9b4d15)

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

This is a known TypeScript footgun — without `Object.setPrototypeOf`, `catch (e) { if (e instanceof APIError) }` silently fails. Anthropic handles it correctly across all error subclasses.

## Branded Types for IDs

Internal types use branded types (nominal typing via intersection with a unique symbol) to prevent mixing different ID types — a message ID cannot be accidentally used where a content block ID is expected. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

```typescript
type MessageId = string & { readonly __brand: "MessageId" };
type ContentBlockId = string & { readonly __brand: "ContentBlockId" };
```

This is a compile-time-only construct — at runtime these are plain strings. The branding prevents accidental interchange without any runtime overhead.

## `readonly` by Default on Response Types

Response interfaces use `readonly` on all properties, signaling that response objects are immutable data structures, not mutable state containers. This aligns with the Python SDK's use of Pydantic `BaseModel` (which is similarly immutable by convention). [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

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
