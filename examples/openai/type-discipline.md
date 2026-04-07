---
title: "Type Discipline"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym]
related: [naming-conventions, patterns, languages/python, languages/typescript]
last_updated: 2026-04-07
---

# Type Discipline

## SDK: Full Static Typing via Stainless

The Python SDK achieves near-complete type coverage through code generation. Every API response is a Pydantic `BaseModel` with fully annotated fields. Every request parameter set is a `TypedDict` with `Required[]` and `NotRequired[]` markers. Return types are explicit on all public methods. This level of discipline is a property of the Stainless generator, not hand-maintained. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
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

The `Literal` types for string enums enable exhaustive pattern matching in type checkers. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

## SDK: Generic Types for Streaming

`Stream[ChatCompletionChunk]` and `AsyncStream[ChatCompletionChunk]` carry the chunk type through to the consumer. Method overloads handle type branching based on the `stream` parameter, so `mypy` and `pyright` narrow the return type statically. [c7a3e18](https://github.com/openai/openai-python/commit/c7a3e18)

```python
@overload
def create(self, *, stream: Literal[False] = ..., **kwargs) -> ChatCompletion: ...
@overload
def create(self, *, stream: Literal[True], **kwargs) -> Stream[ChatCompletionChunk]: ...
@overload
def create(self, *, stream: bool, **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]: ...
```

## SDK: TypedDict for Request Parameters

Request parameters use `TypedDict` rather than Pydantic models, avoiding the need to construct model instances for every API call. Users pass plain dicts that match the shape; the `TypedDict` provides type checking while keeping the call site ergonomic. [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

```python
class CompletionCreateParams(TypedDict, total=False):
    messages: Required[List[ChatCompletionMessageParam]]
    model: Required[Union[str, Literal["gpt-4", "gpt-4o", "gpt-3.5-turbo"]]]
    frequency_penalty: Optional[float]
    max_tokens: Optional[int]
    temperature: Optional[float]
```

## Node SDK: Strict TypeScript Types

openai-node mirrors the Python SDK's strictness using TypeScript interfaces and discriminated unions. Response types use readonly properties; request types use optional fields with explicit `null` handling. See [[languages/typescript]] for TypeScript-specific patterns. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

## Research Code: Minimal Annotations

Research repos occupy the opposite end of the spectrum. Whisper annotates selectively — `forward` methods have return types but parameters are often implicit. CLIP uses almost no annotations. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```python
# whisper — annotations present but selective
class AudioEncoder(nn.Module):
    def forward(self, x: Tensor) -> Tensor:
        x = F.gelu(self.conv1(x))
        ...

# CLIP — mostly unannotated
class CLIP(nn.Module):
    def encode_image(self, image):
        return self.visual(image.type(self.dtype))
```

The contrast is stark: SDK code achieves 100% annotation coverage via generation, while research code annotates only where it aids readability (typically `Tensor` return types). Neither research repo runs `mypy` in CI. This is the widest typing gap in any org analyzed by gitstyle — most organizations cluster around one end of the spectrum or the other, but OpenAI inhabits both extremes simultaneously.

## tiktoken: Type Stubs Bridging the Rust Boundary

tiktoken provides `.pyi` stub files for its Rust-compiled core, making Rust's type safety visible to Python tooling. This is the cleanest example in the org of typed FFI — the Rust implementation is strongly typed, and the stubs project that information into the Python type system. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```python
# tiktoken/_tiktoken.pyi
class CoreBPE:
    def encode_ordinary(self, text: str) -> list[int]: ...
    def encode(self, text: str, allowed_special: set[str]) -> list[int]: ...
    def decode_bytes(self, tokens: list[int]) -> bytes: ...
```

## gym: Protocol-Style Interfaces (Pre-Protocol Era)

Gym's `Env` base class predates Python's `Protocol` type but functions as one, defining the expected interface through concrete methods that raise `NotImplementedError`. The `step()` return type — a 5-tuple of `(observation, reward, terminated, truncated, info)` — is one of the most precisely typed signatures in the research codebase, because downstream RL algorithms depend on this exact shape. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
class Env:
    observation_space: Space
    action_space: Space

    def step(self, action) -> Tuple[ObsType, float, bool, bool, dict]:
        raise NotImplementedError

    def reset(self) -> Tuple[ObsType, dict]:
        raise NotImplementedError
```

## Validation: Pydantic in SDKs, Asserts in Research

SDK validation leverages Pydantic's validators — invalid API responses raise `pydantic.ValidationError` with field-level messages. Research code uses bare `assert` statements for precondition checking. The org accepts this divergence: production code gets strict runtime validation, research code gets lightweight assertions. [e5b7c41](https://github.com/openai/openai-python/commit/e5b7c41)
