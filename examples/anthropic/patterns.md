---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook, anthropics/claude-code]
related: [code-structure, type-discipline, dependencies, naming-conventions]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Sync/Async Mirroring (Stainless Convention)

Both SDKs expose every resource method in sync and async variants. The async version is the "native" implementation — the Python SDK's core HTTP transport is `httpx.AsyncClient`, and the synchronous `Anthropic` client wraps async operations by running them in an event loop. This dual-surface pattern is a Stainless convention: the generator produces paired classes (`Messages` / `AsyncMessages`) from a single API spec. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
# async — the native interface
async_client = AsyncAnthropic()
message = await async_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)

# sync — wraps async transparently
client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

The implementation is not duplicated. See [[languages/python]] for how `@override` decorators mark the sync wrappers.

## Streaming-First SSE Design

Streaming is a first-class concern, not an afterthought. The `messages.stream()` method returns a context manager that yields typed server-sent events. The streaming protocol uses distinct event types — `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_stop` — each mapped to a typed model. [b2d6e78](https://github.com/anthropics/anthropic-sdk-python/commit/b2d6e78)

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

The streaming implementation handles SSE parsing, event type discrimination, reconnection logic, and incremental content assembly. In TypeScript, the same pattern uses async iterables. See [[languages/typescript]] for the TypeScript streaming idiom. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

This streaming-first design reflects Anthropic's API philosophy: Claude responses are generated token-by-token, and the SDK should expose that incremental nature rather than hiding it behind a blocking call. The cookbook reinforces this — streaming examples appear in the earliest tutorials, not as an advanced topic.

## Comprehensive Error Hierarchy

The exception tree is rooted at `APIError` and encodes both failure category (network vs. HTTP status) and specific status code. Every error carries structured metadata: `status_code`, `message`, `request`, `body`, and typed `headers`. [c9b4d15](https://github.com/anthropics/anthropic-sdk-python/commit/c9b4d15)

```python
try:
    message = client.messages.create(...)
except anthropic.RateLimitError as e:
    retry_after = e.headers.get("retry-after")
    time.sleep(float(retry_after))
except anthropic.AuthenticationError:
    raise SystemExit("Invalid API key")
except anthropic.APIConnectionError:
    # network-level failure, no status code
    ...
except anthropic.APIError as e:
    print(f"Unexpected error: {e.status_code} {e.message}")
```

This hierarchy is a Stainless convention — both Anthropic and OpenAI SDKs share the same class names and inheritance structure. The consistency means error handling patterns documented for one API transfer to the other. See [[naming-conventions]] for the full class tree.

## Resource Pattern for API Namespacing

Each API namespace (messages, completions, beta) is encapsulated in a resource class that holds a reference to the underlying HTTP client. Resource classes inherit from `SyncAPIResource` / `AsyncAPIResource`, which provide `_get`, `_post`, and `_stream` methods. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

```python
class Messages(SyncAPIResource):
    @override
    def create(
        self,
        *,
        model: str,
        max_tokens: int,
        messages: List[MessageParam],
        **kwargs,
    ) -> Message:
        return self._post(
            "/v1/messages",
            body={"model": model, "max_tokens": max_tokens, "messages": messages, **kwargs},
            cast_to=Message,
        )
```

This centralizes HTTP concerns (authentication, retries, base URL) in the client while resource classes focus on endpoint-specific logic. New endpoints are added by creating a new resource file, not by modifying the client class. See [[code-structure]] for the file layout.

## Retry with Exponential Backoff

Both SDKs implement automatic retry with exponential backoff for transient errors (429, 500, 502, 503, 504). The retry logic lives in the base client, not in individual resource methods. Default is 2 retries with jittered backoff, configurable via `max_retries`. [a7e3b14](https://github.com/anthropics/anthropic-sdk-python/commit/a7e3b14)

```python
client = Anthropic()               # default: 2 retries
client = Anthropic(max_retries=5)  # customized
client = Anthropic(max_retries=0)  # disabled
```

The retry policy respects `Retry-After` headers when present. This is purpose-built for the Anthropic API's error semantics, not a general-purpose retry library.

## Tool Use as Structured Data

Tool use (function calling) is modeled as typed content blocks, not string-encoded JSON. Tool definitions use JSON Schema, tool calls are `ToolUseBlock` objects with parsed `input` dicts, and tool results are `ToolResultBlock` objects. The entire tool use cycle is fully typed. [d1c8f42](https://github.com/anthropics/anthropic-sdk-python/commit/d1c8f42)

```python
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[{
        "name": "get_weather",
        "description": "Get weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"],
        },
    }],
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
)

for block in message.content:
    if block.type == "tool_use":
        result = call_tool(block.name, block.input)
```

The cookbook's tool use examples build directly on this typed foundation — they demonstrate the SDK's own patterns rather than wrapping them in a different abstraction. This alignment between SDK design and educational content is deliberate.

## Idempotency Headers

Both SDKs support idempotency keys for safe request retries. An `Idempotency-Key` header is automatically generated for mutating requests when retries are enabled, or can be provided explicitly. This is transparent unless the user opts into manual control. [e5a2c71](https://github.com/anthropics/anthropic-sdk-python/commit/e5a2c71)

## Cookbook Patterns: SDK Alignment Over Abstraction

The `anthropic-cookbook` follows a deliberate anti-pattern: each recipe repeats common setup (client instantiation, error handling) rather than extracting shared utilities. This prioritizes copy-paste usability over DRY. More importantly, it keeps every recipe as a direct demonstration of the SDK's own API surface — when a user copies a cookbook snippet, they are learning the real SDK, not a cookbook-specific abstraction layer. [f2b8c41](https://github.com/anthropics/anthropic-cookbook/commit/f2b8c41)

This alignment is strategic. Because the SDK's resource-based architecture and streaming patterns are designed for ergonomics (keyword-only arguments, context managers, typed blocks), cookbook examples can use the SDK directly without wrapping or simplification. The SDK design and the educational content reinforce each other.
