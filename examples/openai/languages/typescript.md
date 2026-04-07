---
title: "TypeScript Idioms"
category: language
confidence: high
sources: [openai/openai-node]
related: [naming-conventions, type-discipline, patterns, dependencies]
last_updated: 2026-04-07
---

# TypeScript Idioms

## Stainless-Generated Architecture

openai-node is Stainless-generated and shares architectural DNA with the Python SDK. The TypeScript idioms here are largely prescribed by the generator, but they represent the patterns OpenAI ships to production users. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

## Resource Classes with Method Overloads

Each API resource is a class with typed methods. The overload pattern mirrors Python's `@overload` — the `stream` parameter value determines the return type at the type level. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

```typescript
export class Completions extends APIResource {
  create(
    body: ChatCompletionCreateParamsNonStreaming,
    options?: Core.RequestOptions,
  ): APIPromise<ChatCompletion>;
  create(
    body: ChatCompletionCreateParamsStreaming,
    options?: Core.RequestOptions,
  ): APIPromise<Stream<ChatCompletionChunk>>;
  create(
    body: ChatCompletionCreateParams,
    options?: Core.RequestOptions,
  ): APIPromise<ChatCompletion> | APIPromise<Stream<ChatCompletionChunk>> {
    return this._client.post('/chat/completions', { body, ...options, stream: body.stream ?? false });
  }
}
```

## Discriminated Unions for Polymorphic Responses

Response types use discriminated unions where the API returns polymorphic objects. The `role` field discriminates message types, allowing `switch(message.role)` to narrow the type. [f4b2a19](https://github.com/openai/openai-node/commit/f4b2a19)

```typescript
export type ChatCompletionMessageParam =
  | ChatCompletionSystemMessageParam
  | ChatCompletionUserMessageParam
  | ChatCompletionAssistantMessageParam
  | ChatCompletionToolMessageParam;

export interface ChatCompletionSystemMessageParam {
  role: 'system';
  content: string;
}

export interface ChatCompletionUserMessageParam {
  role: 'user';
  content: string | Array<ChatCompletionContentPart>;
}
```

## Namespace-Based Type Organization

Types are organized using TypeScript namespaces mirroring the resource hierarchy, supporting both `OpenAI.Chat.Completions.ChatCompletion` as a fully qualified path and direct imports. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

## AsyncIterable for Streaming

Streaming responses implement `AsyncIterable`, enabling `for await...of` consumption. The `Stream` class also exposes `.controller` for `AbortController` integration and `.toReadableStream()` for Web Streams API compatibility. [c9a1e72](https://github.com/openai/openai-node/commit/c9a1e72)

```typescript
const stream = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Count to 10' }],
  stream: true,
});
for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || '');
}
```

## Error Hierarchy Mirroring Python

The error classes mirror the Python SDK exactly. Each extends `APIError` with typed `status`, `error`, and `message` properties. [d7e3b28](https://github.com/openai/openai-node/commit/d7e3b28)

```typescript
export class APIError extends Error {
  readonly status: number | undefined;
  readonly error: Object | undefined;
}
export class AuthenticationError extends APIError { readonly status: 401; }
export class RateLimitError extends APIError { readonly status: 429; }
```

## Options Object Pattern

Every method accepts an optional `RequestOptions` last argument for per-request transport configuration (timeouts, headers, abort signals), keeping API parameter types clean of transport concerns. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

```typescript
interface RequestOptions {
  headers?: Headers;
  maxRetries?: number;
  timeout?: number;
  signal?: AbortSignal;
  httpAgent?: Agent;
}

await client.chat.completions.create(
  { model: 'gpt-4', messages: [...] },
  { timeout: 30000, signal: controller.signal }
);
```

## Strict Compilation, No `any`

The SDK compiles with `strict: true` including `strictNullChecks`. The codebase avoids `any` — genuinely unknown types use `unknown` instead. [f4b2a19](https://github.com/openai/openai-node/commit/f4b2a19)

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2018",
    "module": "commonjs",
    "moduleResolution": "node",
    "declaration": true
  }
}
```

## Dual CJS/ESM Output

openai-node ships both CommonJS and ES Module builds via conditional exports in `package.json`. [a2d8c13](https://github.com/openai/openai-node/commit/a2d8c13)

```json
{
  "exports": {
    ".": {
      "import": "./dist/esm/index.js",
      "require": "./dist/cjs/index.js"
    }
  }
}
```

## Runtime Environment Detection

The SDK detects its runtime (Node.js, Deno, Bun, Cloudflare Workers, Vercel Edge) and adjusts behavior — native `fetch` in edge environments, `node-fetch` in older Node.js. Detection happens at import time. [c9a1e72](https://github.com/openai/openai-node/commit/c9a1e72)
