---
title: "Naming Conventions"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook]
related: [code-structure, type-discipline, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Naming Conventions

## PascalCase for API Models

All Pydantic models and TypeScript interfaces representing API objects use PascalCase: `Message`, `ContentBlock`, `TextBlock`, `ToolUseBlock`, `MessageCreateParams`, `MessageStreamEvent`. The name matches the API schema definition exactly, creating a 1:1 mapping between documentation and code. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

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

Compound names follow the pattern `{Resource}{Action}{Suffix}`: `MessageCreateParams`, `MessageStreamEvent`, `ContentBlockDeltaEvent`. This makes it possible to infer the type name from the API endpoint and vice versa.

## snake_case for Methods and Modules

Python SDK methods use snake_case: `messages.create()`, `messages.stream()`, `completions.create()`. Module filenames are snake_case: `message_create_params.py`, `content_block.py`. This follows PEP 8 exactly — no exceptions, no mixed conventions. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

The TypeScript SDK uses camelCase for methods (`messages.create()`, `messages.stream()`) and kebab-case for filenames (`message-create-params.ts`), following standard TypeScript/Node conventions. See [[languages/typescript]] for details.

## Underscore Prefix for Internal Modules

Anthropic uses a strict underscore-prefix convention to separate public and private API surfaces. Internal implementation modules are prefixed with `_`: `_client.py`, `_streaming.py`, `_exceptions.py`, `_base_client.py`, `_resource.py`. Public re-exports happen through `__init__.py`. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```
anthropic/
  __init__.py          # public — re-exports everything
  _client.py           # internal — Anthropic class definition
  _base_client.py      # internal — shared HTTP logic
  _streaming.py        # internal — Stream/AsyncStream implementation
  _exceptions.py       # internal — error hierarchy
  _resource.py         # internal — base resource class
  resources/           # public — resource modules
  types/               # public — type definitions
```

This convention means `from anthropic import Anthropic` works, but `from anthropic._client import Anthropic` triggers linter warnings. The underscore prefix is the public API boundary.

## Hierarchical Error Names

Error classes follow a strict naming hierarchy rooted at `APIError`. Each error class name encodes its semantic meaning: `AuthenticationError`, `PermissionDeniedError`, `NotFoundError`, `RateLimitError`, `InternalServerError`, `APIConnectionError`, `APITimeoutError`. [c9b4d15](https://github.com/anthropics/anthropic-sdk-python/commit/c9b4d15)

```python
class APIError(Exception): ...
class APIConnectionError(APIError): ...
class APITimeoutError(APIConnectionError): ...
class APIStatusError(APIError): ...
class AuthenticationError(APIStatusError): ...
class PermissionDeniedError(APIStatusError): ...
class NotFoundError(APIStatusError): ...
class RateLimitError(APIStatusError): ...
class UnprocessableEntityError(APIStatusError): ...
class InternalServerError(APIStatusError): ...
```

The hierarchy maps to HTTP semantics: `APIStatusError` is the parent for all HTTP-status-based errors, `APIConnectionError` for transport-level failures. Both SDKs use identical error class names. See [[patterns]] for error handling conventions.

## Param Suffix for Request Types

Types representing API request bodies are suffixed with `Params`: `MessageCreateParams`, `CompletionCreateParams`. Types representing API response bodies have no suffix — they are just the noun: `Message`, `Completion`. This makes it immediately clear whether a type is input or output. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
# input type — Params suffix
class MessageCreateParams(TypedDict):
    model: Required[str]
    max_tokens: Required[int]
    messages: Required[List[MessageParam]]

# output type — no suffix
class Message(BaseModel):
    id: str
    content: List[ContentBlock]
    ...
```

## Event Suffix for Streaming Types

Server-sent event types use the `Event` suffix: `MessageStartEvent`, `ContentBlockDeltaEvent`, `MessageStopEvent`, `MessageStreamEvent`. The event name matches the SSE `event:` field, making it straightforward to map protocol events to typed objects. [b2d6e78](https://github.com/anthropics/anthropic-sdk-python/commit/b2d6e78)

## `__all__` as the Canonical Export List

Every public Python module defines `__all__`, and the list is maintained alphabetically. This is not just convention — it is the authoritative record of what the module exports. Adding a new public type requires updating `__all__` in both the defining module and the root `__init__.py`. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

```python
__all__ = [
    "APIConnectionError",
    "APIError",
    "APIStatusError",
    "APITimeoutError",
    "Anthropic",
    "AsyncAnthropic",
    "AuthenticationError",
    ...
]
```

## Async Prefix for Async Variants

Async client and resource classes are prefixed with `Async`: `AsyncAnthropic`, `AsyncMessages`, `AsyncCompletions`, `AsyncStream`. The sync class always comes first in file ordering and documentation. This pattern is consistent across every resource module. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)
