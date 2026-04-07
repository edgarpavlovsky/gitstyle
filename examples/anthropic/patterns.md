---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook, anthropics/claude-code]
related: [code-structure, type-discipline, dependencies, naming-conventions]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Async-First with Sync Wrappers

Anthropic's SDKs are designed async-first. The core HTTP transport in the Python SDK is built on `httpx.AsyncClient`, and the synchronous `Anthropic` client wraps async operations. Every resource method exists in both sync and async variants, with the async version being the "native" implementation. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
# async is the primary interface
async_client = AsyncAnthropic()
message = await async_client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)

# sync wraps async transparently
client = Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

The sync wrapper runs the async code in an event loop, so the implementation is not duplicated. Resource classes come in pairs: `Messages` / `AsyncMessages`, `Completions` / `AsyncCompletions`. See [[languages/python]] for how `@override` decorators mark the sync overrides.

## Streaming-First SSE Design

Streaming is a first-class concern, not an afterthought bolted onto a request/response SDK. The `messages.stream()` method returns a context manager that yields typed server-sent events. The streaming protocol uses distinct event types — `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_stop` — each mapped to a Pydantic model. [b2d6e78](https://github.com/anthropics/anthropic-sdk-python/commit/b2d6e78)

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

The streaming implementation handles SSE parsing, event type discrimination, reconnection logic, and incremental content assembly. In the TypeScript SDK, the same pattern uses async iterables. See [[languages/typescript]] for the TypeScript streaming idiom. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

## Comprehensive Error Hierarchy

Anthropic standardizes a hierarchical exception tree rooted at `APIError`. The hierarchy encodes both the failure category (network vs. HTTP status) and the specific HTTP status code. Every error carries structured metadata: `status_code`, `message`, `request`, `body`, and typed `headers`. [c9b4d15](https://github.com/anthropics/anthropic-sdk-python/commit/c9b4d15)

```python
try:
    message = client.messages.create(...)
except anthropic.RateLimitError as e:
    # e.status_code == 429
    # e.headers["retry-after"] available
    retry_after = e.headers.get("retry-after")
    time.sleep(float(retry_after))
except anthropic.AuthenticationError:
    # e.status_code == 401
    raise SystemExit("Invalid API key")
except anthropic.APIConnectionError:
    # network-level failure, no status code
    ...
except anthropic.APIError as e:
    # catch-all for any API error
    print(f"Unexpected error: {e.status_code} {e.message}")
```

Both SDKs implement the identical hierarchy. Error class names, inheritance structure, and attached metadata are consistent across Python and TypeScript. This allows documentation and error handling guides to be language-agnostic. See [[naming-conventions]] for the full class tree.

## Pydantic Models for Request/Response Typing

All API request and response objects are modeled as Pydantic `BaseModel` subclasses (Python) or equivalent typed interfaces (TypeScript). This provides runtime validation, serialization, and IDE completion in one layer. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```python
class Message(BaseModel):
    id: str
    type: Literal["message"]
    role: Literal["assistant"]
    content: List[ContentBlock]
    model: str
    stop_reason: Optional[StopReason]
    stop_sequence: Optional[str]
    usage: Usage
```

Response models use `BaseModel` (immutable, validated). Request parameter types use `TypedDict` with `Required[]` markers, since request bodies are constructed by the user and don't need validation on the SDK side — only the structure hint. This split is deliberate: responses are parsed and validated, requests are just typed hints. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

## Resource Pattern for API Namespacing

Each API namespace (messages, completions, beta features) is encapsulated in a resource class that holds a reference to the underlying HTTP client. Resource classes inherit from a thin `SyncAPIResource` / `AsyncAPIResource` base that provides `_get`, `_post`, and `_stream` methods. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

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

This pattern centralizes HTTP concerns (authentication, retries, base URL) in the client while letting resource classes focus on endpoint-specific logic. New endpoints are added by creating a new resource file, not by modifying the client class. See [[code-structure]] for the file layout.

## Retry with Exponential Backoff

Both SDKs implement automatic retry with exponential backoff for transient errors (429, 500, 502, 503, 504). The retry logic lives in the base client, not in individual resource methods. Default behavior is 2 retries with jittered backoff, configurable via `max_retries` on the client constructor. [a7e3b14](https://github.com/anthropics/anthropic-sdk-python/commit/a7e3b14)

```python
# default: 2 retries
client = Anthropic()

# customized
client = Anthropic(max_retries=5)

# disable retries
client = Anthropic(max_retries=0)
```

The retry policy respects `Retry-After` headers when present. This is not a general-purpose retry library — it is purpose-built for the Anthropic API's specific error semantics.

## Tool Use as Structured Data

Tool use (function calling) is modeled as typed content blocks, not string-encoded JSON. Tool definitions use JSON Schema, tool calls are `ToolUseBlock` objects with parsed `input` dicts, and tool results are `ToolResultBlock` objects. The entire tool use cycle is fully typed from definition through execution. [d1c8f42](https://github.com/anthropics/anthropic-sdk-python/commit/d1c8f42)

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
        # block.name, block.input are typed
        result = call_tool(block.name, block.input)
```

## Cookbook Patterns: Self-Contained Recipes

The `anthropic-cookbook` follows a pattern where each example is a self-contained recipe with no shared imports from other recipes. Common patterns (client setup, error handling) are repeated in each recipe rather than extracted into a shared utility module. This prioritizes copy-paste usability over DRY. [f2b8c41](https://github.com/anthropics/anthropic-cookbook/commit/f2b8c41)

## Idempotency Headers

Anthropic's SDKs support idempotency keys for safe request retries. The pattern is implemented at the client level — an `Idempotency-Key` header is automatically generated for mutating requests when retries are enabled, or can be provided explicitly. This is transparent to the user unless they opt into manual control. [e5a2c71](https://github.com/anthropics/anthropic-sdk-python/commit/e5a2c71)
