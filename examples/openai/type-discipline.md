---
title: "Type Discipline"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym]
related: [naming-conventions, patterns, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Type Discipline

## SDK: Full Static Typing with Pydantic

The Python SDK achieves near-complete type coverage. Every API response is a Pydantic `BaseModel` with fully annotated fields. Every request parameter set is a `TypedDict` with `Required[]` and `NotRequired[]` markers. Return types are explicit on all public methods. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
# types/chat/chat_completion.py — every field typed
class ChatCompletion(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: Literal["chat.completion"]
    system_fingerprint: Optional[str] = None
    usage: Optional[CompletionUsage] = None

class Choice(BaseModel):
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter"]
    index: int
    message: ChatCompletionMessage
    logprobs: Optional[ChoiceLogprobs] = None
```

The use of `Literal` types for string enums (like `finish_reason`) enables exhaustive pattern matching in type checkers. This level of typing discipline is Stainless-generated and represents the strictest end of the organization's spectrum. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

## SDK: Generic Types for Streaming

OpenAI uses generic types to distinguish streaming from non-streaming responses. `Stream[ChatCompletionChunk]` and `AsyncStream[ChatCompletionChunk]` carry the chunk type through to the consumer. Method overloads handle the type branching based on the `stream` parameter. [c7a3e18](https://github.com/openai/openai-python/commit/c7a3e18)

```python
# overloaded signatures for type narrowing
@overload
def create(self, *, stream: Literal[False] = ..., **kwargs) -> ChatCompletion: ...
@overload
def create(self, *, stream: Literal[True], **kwargs) -> Stream[ChatCompletionChunk]: ...
@overload
def create(self, *, stream: bool, **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]: ...

def create(self, *, stream=False, **kwargs):
    ...
```

This `@overload` pattern means `mypy` and `pyright` can narrow the return type statically based on the `stream` argument value — a consumer passing `stream=True` gets `Stream[ChatCompletionChunk]` without casting.

## SDK: TypedDict for Request Parameters

Request parameters use `TypedDict` rather than Pydantic models. This avoids requiring users to construct model instances for every API call — they can pass plain dicts that match the shape. The `TypedDict` provides type checking while keeping the call-site ergonomic. [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

```python
class CompletionCreateParams(TypedDict, total=False):
    messages: Required[List[ChatCompletionMessageParam]]
    model: Required[Union[str, Literal["gpt-4", "gpt-4o", "gpt-3.5-turbo"]]]
    frequency_penalty: Optional[float]
    max_tokens: Optional[int]
    n: Optional[int]
    stream: Optional[bool]
    temperature: Optional[float]
```

## Node SDK: Strict TypeScript Types

openai-node mirrors the Python SDK's type strictness using TypeScript interfaces and discriminated unions. Response types are interfaces with readonly properties. Request types use optional fields with explicit `null` handling. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

```typescript
export interface ChatCompletion {
  id: string;
  choices: Array<ChatCompletion.Choice>;
  created: number;
  model: string;
  object: 'chat.completion';
  system_fingerprint?: string | null;
  usage?: CompletionUsage | null;
}
```

See [[languages/typescript]] for TypeScript-specific type patterns.

## Research Code: Minimal Annotations

Research repositories occupy the opposite end of the typing spectrum. Whisper uses type annotations sparingly — `forward` methods have annotated return types but parameter types are often implicit. CLIP uses almost no type annotations. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```python
# whisper/model.py — annotations present but selective
class AudioEncoder(nn.Module):
    def forward(self, x: Tensor) -> Tensor:
        x = F.gelu(self.conv1(x))
        ...

# CLIP/clip/model.py — mostly unannotated
class CLIP(nn.Module):
    def encode_image(self, image):
        return self.visual(image.type(self.dtype))

    def encode_text(self, text):
        ...
```

The contrast is stark: SDK code achieves 100% annotation coverage via code generation, while research code annotates only where it aids readability (typically `Tensor` return types). Neither repo runs `mypy` in CI. See [[testing]] for CI patterns.

## tiktoken: Type Stubs for Rust Boundary

tiktoken provides `.pyi` type stub files for the Rust-compiled core module. The Rust code itself is strongly typed, and the stubs expose that information to Python type checkers. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```python
# tiktoken/_tiktoken.pyi
class CoreBPE:
    def encode_ordinary(self, text: str) -> list[int]: ...
    def encode(self, text: str, allowed_special: set[str]) -> list[int]: ...
    def decode_bytes(self, tokens: list[int]) -> bytes: ...
```

This `.pyi` pattern bridges the Rust/Python type boundary — the Rust implementation is type-safe, and the stubs make that safety visible to Python tooling.

## gym: Protocol-Style Interfaces (Pre-Protocol Era)

Gym's `Env` base class predates Python's `Protocol` type but functions as one. It defines the expected interface through concrete methods that raise `NotImplementedError`. The `spaces` module uses generic types (`Space[np.ndarray]`) for observation and action spaces. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
class Env:
    observation_space: Space
    action_space: Space

    def step(self, action) -> Tuple[ObsType, float, bool, bool, dict]:
        raise NotImplementedError

    def reset(self) -> Tuple[ObsType, dict]:
        raise NotImplementedError
```

The return type of `step()` is one of the most precisely typed signatures in the research codebase — a 5-tuple of `(observation, reward, terminated, truncated, info)` — because downstream RL algorithms depend on this exact shape.

## Validation: Pydantic in SDKs, Asserts in Research

SDK validation leverages Pydantic's built-in validators. Invalid API responses raise `pydantic.ValidationError` with detailed field-level error messages. Research code uses bare `assert` statements for precondition checking. [e5b7c41](https://github.com/openai/openai-python/commit/e5b7c41)

```python
# SDK: Pydantic handles validation automatically
response = ChatCompletion.model_validate(json_data)
# raises ValidationError if shape doesn't match

# Research: assert-based preconditions
assert audio.shape[-1] <= N_SAMPLES, "audio is too long"
assert x.dtype == torch.float32
```

The organization accepts this divergence — production SDK code gets strict runtime validation, research code gets lightweight assertions. See [[patterns]] for error handling patterns.
