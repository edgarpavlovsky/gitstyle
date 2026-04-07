---
title: "Type Discipline"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook]
related: [naming-conventions, patterns, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Type Discipline

## Exhaustive Type Hints in Python

The Python SDK annotates every public function signature, every class attribute, and every return type. This is not selective typing — it is exhaustive. Method signatures include `Literal` types for string enums, `Optional` for nullable fields, `Union` for polymorphic content blocks, and `overload` decorators for methods with multiple return type signatures. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```python
def create(
    self,
    *,
    model: str,
    max_tokens: int,
    messages: Iterable[MessageParam],
    metadata: Optional[MessageCreateParams.Metadata] = None,
    stop_sequences: Optional[List[str]] = None,
    stream: Optional[Literal[False]] = None,
    system: Optional[Union[str, Iterable[TextBlockParam]]] = None,
    temperature: Optional[float] = None,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
) -> Message:
    ...
```

No `Any` escape hatches in public API signatures. `Any` appears only in internal helper modules (`_compat.py`, `_utils.py`) where Python's type system genuinely cannot express the constraint. The public types directory and resource modules are `Any`-free. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)

## Literal Types Over Enums

Rather than Python `Enum` classes, Anthropic uses `Literal` types for string-valued enumerations. This keeps the runtime representation as plain strings while providing static type checking. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```python
StopReason = Literal["end_turn", "max_tokens", "stop_sequence", "tool_use"]
MessageRole = Literal["user", "assistant"]
ContentBlockType = Literal["text", "tool_use", "tool_result", "image"]
```

Users pass plain strings (`"end_turn"`) and get plain strings back, but mypy and pyright catch typos at analysis time. No serialization overhead, no `.value` access, no import required at the call site. This is a Stainless convention that works especially well for generated SDKs — the `Literal` types are derived directly from the OpenAPI spec's enum definitions.

## TypeScript Strict Mode

The TypeScript SDK enables `strict: true` in `tsconfig.json`, activating `strictNullChecks`, `strictFunctionTypes`, `noImplicitAny`, and related flags. No `// @ts-ignore` or `as any` casts in the public codebase. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

See [[languages/typescript]] for how strict mode interacts with the SDK's generic resource typing and `noUncheckedIndexedAccess`.

## Discriminated Unions for Content Blocks

Both SDKs use discriminated unions (tagged unions) to model polymorphic API responses. Content blocks are typed as `Union[TextBlock, ToolUseBlock]` in Python and `TextBlock | ToolUseBlock` in TypeScript, with the `type` field as the discriminant. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

```python
ContentBlock = Union[TextBlock, ToolUseBlock]

class TextBlock(BaseModel):
    type: Literal["text"]
    text: str

class ToolUseBlock(BaseModel):
    type: Literal["tool_use"]
    id: str
    name: str
    input: dict
```

After checking `block.type == "text"`, type checkers know `block` is a `TextBlock` and allow `.text` access without casts. The pattern carries through to streaming events, where `MessageStreamEvent` is a union discriminated on `type`. This is where the `Literal` types over enums decision pays off — discriminated union narrowing works cleanly with string literals.

## BaseModel for Responses, TypedDict for Requests

Response models inherit from Pydantic `BaseModel`, providing runtime validation and JSON parsing. When the API returns a response, it is parsed through the model, which validates types, coerces compatible values, and raises `ValidationError` on schema mismatches. The `extra="allow"` config enables forward compatibility — unknown fields from API updates are silently accepted. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

Request parameter types use `TypedDict` with `Required[]` markers. This is deliberate: request bodies are constructed by the user and validated by the API server, not the SDK. `TypedDict` provides IDE completion and static checking without runtime overhead. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

```python
class MessageCreateParams(TypedDict, total=False):
    model: Required[str]
    max_tokens: Required[int]
    messages: Required[Iterable[MessageParam]]
    metadata: Optional[MessageCreateParams.Metadata]
    stop_sequences: Optional[List[str]]
    stream: Optional[bool]
    temperature: Optional[float]
```

The `total=False` with selective `Required[]` means only mandatory parameters must be provided. Optional parameters can be omitted entirely rather than set to `None`. This split — immutable validated responses, lightweight typed requests — is a Stainless pattern that matches API SDK semantics precisely.

## Generic Resource Typing

Resource classes use generic type parameters to express the relationship between request parameters and response types. The base `_post` method is generic over the response type, so each resource method's return type is inferred from the `cast_to` argument. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

```python
class SyncAPIResource:
    def _post(
        self,
        path: str,
        *,
        body: object,
        cast_to: Type[_T],
        **kwargs,
    ) -> _T:
        ...
```

This eliminates manual casting. When `Messages.create` calls `self._post(..., cast_to=Message)`, the return type is inferred as `Message` without an explicit annotation. The type flows through the generic.

## Cross-SDK Type Philosophy

The typing strategies in Python and TypeScript serve the same goal through different mechanisms. Python uses Pydantic `BaseModel` for runtime validation and `Literal` types for static narrowing. TypeScript uses `readonly` interfaces for immutability and discriminated unions for compile-time exhaustiveness. Both avoid escape hatches (`Any` in Python, `any` in TypeScript) in public APIs. The result: users in either language get full IDE completion, catch typos at analysis time, and can trust the types to match the API wire format. This cross-language type parity is what makes "write documentation once, transliterate between languages" viable for Anthropic's developer relations team.
