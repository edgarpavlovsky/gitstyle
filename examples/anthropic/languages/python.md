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

Anthropic's Python SDK uses the `@override` decorator (from `typing_extensions`) on every method that overrides a parent class method. This makes inheritance relationships explicit at the call site and enables static analysis tools to verify the override is valid. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

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

Every sync resource method that wraps the async implementation uses `@override`. This is not optional — the CI type checker (pyright) flags missing `@override` decorators when the base class method exists.

## `__all__` in Every Public Module

Every module under `anthropic/` that exports public symbols defines `__all__`. The list is maintained in alphabetical order. This is not just a convention — it is enforced by the test suite, which verifies that all names in `__all__` are actually defined in the module. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

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

Public SDK methods use keyword-only arguments (the `*` separator) for all parameters after the implicit `self`. This prevents positional argument mistakes and makes call sites self-documenting. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

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

Users must write `client.messages.create(model="...", max_tokens=1024, messages=[...])` — positional calls like `client.messages.create("...", 1024, [...])` raise `TypeError`. This is consistent across every resource method.

## Pydantic BaseModel with `extra="allow"`

All response models inherit from `BaseModel` with `model_config = ConfigDict(extra="allow")`. This forward-compatibility pattern means the SDK won't break when the API adds new fields to existing responses. Unknown fields are silently accepted and accessible via `model_extra`. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

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

This pattern prevents resource leaks. Direct iteration without a context manager is not supported — the SDK forces the safe path.

## `Iterable` Over `List` for Input Parameters

Input parameters that accept sequences use `Iterable[T]` rather than `List[T]`. This allows users to pass lists, tuples, generators, or any iterable without conversion. The SDK iterates the input once during serialization. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

```python
def create(
    self,
    *,
    messages: Iterable[MessageParam],  # not List[MessageParam]
    ...
) -> Message:
```

## `Optional` Over Default `None`

Parameters that can be omitted use `Optional[T] = None` rather than `T | None = None`. The SDK targets Python 3.8+ compatibility, so the `X | Y` union syntax (Python 3.10+) is avoided in the codebase. `typing_extensions` backports are used for newer constructs. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

## Ruff for Formatting and Linting

Anthropic standardizes on `ruff` for both Python formatting and linting. Ruff replaces black, isort, and flake8 in a single tool. The configuration lives in `pyproject.toml` with Anthropic's preferred rules. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)

```toml
[tool.ruff]
line-length = 120
target-version = "py38"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

Line length is 120 characters, not the ruff/black default of 88. Imports are sorted with isort-compatible rules. See [[commit-hygiene]] for how ruff is enforced in CI.

## Python 3.8+ as Minimum Version

The SDK supports Python 3.8 and above. This drives several style choices: `typing_extensions` for `Required`, `override`, `Literal`; `Optional[T]` instead of `T | None`; no `match/case` statements. The `pyproject.toml` declares `requires-python = ">=3.8"`. [a7e3b14](https://github.com/anthropics/anthropic-sdk-python/commit/a7e3b14)
