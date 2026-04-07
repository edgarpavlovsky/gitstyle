---
title: "Python Idioms"
category: language
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-cookbook, anthropics/courses]
related: [naming-conventions, type-discipline, patterns, dependencies]
last_updated: 2026-04-07
---

# Python Idioms

## `@override` Decorator on Method Overrides

The Python SDK uses `@override` (from `typing_extensions`) on every method that overrides a parent class method. This makes inheritance explicit and enables pyright to verify the override is valid — a misspelled method name or wrong signature is caught at analysis time. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
from typing_extensions import override

class Messages(SyncAPIResource):
    @override
    def create(
        self,
        *,
        model: str,
        max_tokens: int,
        messages: Iterable[MessageParam],
        **kwargs,
    ) -> Message:
        return self._post("/v1/messages", body={...}, cast_to=Message)
```

In the Stainless-generated code, `@override` marks sync resource methods that wrap the async implementation. The CI type checker (pyright) flags missing `@override` decorators when the base class method exists.

## `__all__` in Every Public Module

Every module under `anthropic/` that exports public symbols defines `__all__`, maintained in alphabetical order. The test suite verifies that all names in `__all__` are actually defined in the module. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

```python
# anthropic/types/__init__.py
__all__ = [
    "ContentBlock",
    "ContentBlockDeltaEvent",
    "ContentBlockStartEvent",
    "ContentBlockStopEvent",
    "Message",
    "MessageCreateParams",
    "MessageParam",
    "MessageStartEvent",
    "MessageStreamEvent",
    "MessageStopEvent",
    "TextBlock",
    "ToolUseBlock",
    "Usage",
]
```

Adding a new type requires updating `__all__` in both the defining module and the re-exporting `__init__.py`. Forgetting either is caught by tests.

## Keyword-Only Arguments with `*`

Public SDK methods use keyword-only arguments (the `*` separator) for all parameters after `self`. This prevents positional argument mistakes and makes call sites self-documenting. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```python
def create(
    self,
    *,                          # everything after this is keyword-only
    model: str,
    max_tokens: int,
    messages: Iterable[MessageParam],
    stream: Optional[bool] = None,
    temperature: Optional[float] = None,
) -> Message:
```

`client.messages.create("claude-sonnet-4-20250514", 1024, [...])` raises `TypeError`. This is consistent across every resource method and is a Stainless convention — the same pattern appears in OpenAI's Python SDK.

## Pydantic BaseModel with `extra="allow"`

All response models use `model_config = ConfigDict(extra="allow")`. Unknown fields from API updates are silently accepted and accessible via `model_extra`. This forward-compatibility pattern means the SDK never breaks when the API adds new response fields. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```python
from pydantic import BaseModel, ConfigDict

class Message(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    type: Literal["message"]
    role: Literal["assistant"]
    content: List[ContentBlock]
    ...
```

See [[type-discipline]] for how this contrasts with `TypedDict` for request parameters.

## Context Managers for Streaming

Streaming responses use context managers (`with` / `async with`) to ensure the underlying HTTP connection is properly closed. The `MessageStream` object implements `__enter__` / `__exit__` and provides both event-level iteration and convenience accessors like `.text_stream`. [b2d6e78](https://github.com/anthropics/anthropic-sdk-python/commit/b2d6e78)

```python
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
# connection is closed here, even if an exception occurred
```

Direct iteration without a context manager is not supported — the SDK forces the safe path. The cookbook examples consistently demonstrate this pattern, reinforcing it as the canonical approach.

## `Iterable` Over `List` for Input Parameters

Input parameters that accept sequences use `Iterable[T]` rather than `List[T]`. Users can pass lists, tuples, generators, or any iterable. The SDK iterates once during serialization. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

```python
def create(
    self,
    *,
    messages: Iterable[MessageParam],  # not List[MessageParam]
    ...
) -> Message:
```

## `Optional` Over Union Syntax

Parameters that can be omitted use `Optional[T] = None` rather than `T | None = None`. The SDK targets Python 3.8+ compatibility, so the `X | Y` union syntax (Python 3.10+) is avoided. `typing_extensions` backports are used for newer constructs. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

## Ruff for Formatting and Linting

Anthropic standardizes on `ruff` for both formatting and linting, replacing black, isort, and flake8. Configuration lives in `pyproject.toml`. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)

```toml
[tool.ruff]
line-length = 120
target-version = "py38"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

Line length is 120 characters, not the ruff/black default of 88. See [[commit-hygiene]] for how ruff is enforced in CI.

## Python 3.8+ as Minimum Version

The SDK supports Python 3.8+. This drives several style choices: `typing_extensions` for `Required`, `override`, `Literal`; `Optional[T]` instead of `T | None`; no `match/case` statements. The `pyproject.toml` declares `requires-python = ">=3.8"`. [a7e3b14](https://github.com/anthropics/anthropic-sdk-python/commit/a7e3b14)
