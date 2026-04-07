---
title: "Type Discipline"
category: style
confidence: high
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook]
related: [naming-conventions, patterns, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Type Discipline

## Comprehensive Type Hints in Python

Anthropic's Python SDK annotates every public function signature, every class attribute, and every return type. This is not selective typing — it is exhaustive. Method signatures include `Literal` types for string enums, `Optional` for nullable fields, `Union` for polymorphic content blocks, and `overload` decorators for methods with multiple return type signatures. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

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

There are no `Any` escape hatches in public API signatures. Internal utilities may use `Any` for truly generic helpers, but the public surface is fully typed. See [[languages/python]] for the typing patterns specific to the Python SDK.

## Literal Types for String Enums

Rather than Python `Enum` classes, Anthropic uses `Literal` types for string-valued enumerations. This keeps the runtime representation as plain strings while providing static type checking. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```python
StopReason = Literal["end_turn", "max_tokens", "stop_sequence", "tool_use"]
MessageRole = Literal["user", "assistant"]
ContentBlockType = Literal["text", "tool_use", "tool_result", "image"]
```

This pattern avoids the serialization overhead and user-facing complexity of enum classes. Users pass plain strings (`"end_turn"`) and get plain strings back, but mypy and pyright still catch typos at analysis time.

## TypeScript Strict Mode Everywhere

The TypeScript SDK enables strict mode in `tsconfig.json`: `strict: true`, which activates `strictNullChecks`, `strictFunctionTypes`, `strictBindCallApply`, `noImplicitAny`, and `noImplicitThis`. There are no `// @ts-ignore` or `as any` casts in the public codebase. [b8e4a19](https://github.com/anthropics/anthropic-sdk-typescript/commit/b8e4a19)

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2020",
    "moduleResolution": "node",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

See [[languages/typescript]] for how strict mode interacts with the SDK's generic resource typing.

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

This enables exhaustive type narrowing: after checking `block.type == "text"`, type checkers know `block` is a `TextBlock` and can access `.text` without casts. The pattern carries through to streaming events, where `MessageStreamEvent` is a union discriminated on `type`.

## Pydantic for Runtime Validation

Response models inherit from Pydantic `BaseModel`, providing both static type checking and runtime validation. When the API returns a response, it is parsed through the Pydantic model, which validates types, coerces compatible values, and raises `ValidationError` on schema mismatches. [d7f3a62](https://github.com/anthropics/anthropic-sdk-python/commit/d7f3a62)

```python
class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

class Message(BaseModel):
    id: str
    type: Literal["message"]
    role: Literal["assistant"]
    content: List[ContentBlock]
    model: str
    stop_reason: Optional[StopReason]
    usage: Usage
```

This dual-layer approach (static types + runtime validation) catches both programmer errors and API contract violations. If the API adds a new field, existing models pass validation via `model_config = ConfigDict(extra="allow")`.

## TypedDict for Request Parameters

Request parameter types use `TypedDict` rather than `BaseModel`. This is a deliberate design choice: request bodies are constructed by the SDK user and should not be validated by the SDK (the API server validates them). `TypedDict` provides IDE completion and static checking without runtime overhead. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

```python
class MessageCreateParams(TypedDict, total=False):
    model: Required[str]
    max_tokens: Required[int]
    messages: Required[Iterable[MessageParam]]
    metadata: Optional[MessageCreateParams.Metadata]
    stop_sequences: Optional[List[str]]
    stream: Optional[bool]
    system: Optional[Union[str, Iterable[TextBlockParam]]]
    temperature: Optional[float]
```

The `total=False` with selective `Required[]` markers means only mandatory parameters must be provided. Optional parameters can be omitted entirely rather than set to `None`.

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

This eliminates manual casting. When `Messages.create` calls `self._post(..., cast_to=Message)`, the return type is inferred as `Message` without an explicit annotation on `create`'s return type. The type flows through.

## No `Any` in Public API

A grep for `Any` across the Python SDK's public surface returns zero results. `Any` appears only in internal helper modules (`_compat.py`, `_utils.py`) where it is genuinely unavoidable due to Python's type system limitations. The public types directory and resource modules are `Any`-free. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)
