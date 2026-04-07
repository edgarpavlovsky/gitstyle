---
title: "Python Idioms"
category: language
confidence: high
sources: [openai/openai-python, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym, openai/openai-cookbook]
related: [naming-conventions, type-discipline, patterns, dependencies]
last_updated: 2026-04-07
---

# Python Idioms

## Two Dialects

OpenAI's Python code exists in two distinct dialects. SDK Python (Stainless-generated) is heavily typed, uses Pydantic, async/await, and targets 3.7+ compatibility. Research Python is PyTorch-oriented, lightly typed, and optimized for readability by ML practitioners. Most idioms below note which dialect they belong to.

## Keyword-Only Parameters (SDK)

All SDK public methods use keyword-only arguments via the `*` separator, preventing positional-argument bugs in APIs with many optional parameters. This is enforced by the Stainless generator. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
def create(
    self,
    *,                          # everything after is keyword-only
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    frequency_penalty: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: Optional[bool] = None,
    temperature: Optional[float] = None,
) -> ChatCompletion:
```

## @overload for Type Narrowing (SDK)

The SDK uses `@typing.overload` extensively for precise return types based on argument values. The `stream` parameter is the canonical example — overloads let type checkers know `stream=True` returns `Stream[...]`. [c7a3e18](https://github.com/openai/openai-python/commit/c7a3e18)

```python
@overload
def create(self, *, stream: Literal[False] = ..., **kwargs) -> ChatCompletion: ...
@overload
def create(self, *, stream: Literal[True], **kwargs) -> Stream[ChatCompletionChunk]: ...

def create(self, *, stream=False, **kwargs):
    ...
```

## __all__ for Public API Control (SDK)

SDK modules define `__all__` to control star imports and make the public API surface explicit. Internal modules (prefixed with `_`) are excluded from `__all__` in the package `__init__.py`. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

## Dataclass Configuration (Research)

Research repos use `@dataclass` for model configuration — no `attrs`, no Pydantic, no config files. This mirrors broader PyTorch community convention. See [[type-discipline]] for the SDK/research typing contrast. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```python
@dataclass
class ModelDimensions:
    n_mels: int
    n_audio_ctx: int
    n_audio_state: int
    n_audio_head: int
    n_audio_layer: int
```

## torch.nn.functional Preference (Research)

Research code prefers the functional API (`F.gelu`, `F.softmax`, `F.cross_entropy`) for stateless operations, reserving `nn.Module` subclasses for layers with learnable parameters. Standard PyTorch convention, consistent across Whisper, CLIP, and gym. [e7f2c83](https://github.com/openai/whisper/commit/e7f2c83)

```python
import torch.nn.functional as F

x = F.gelu(self.conv1(x))          # functional for stateless ops
self.conv1 = nn.Conv1d(...)          # module for layers with weights
```

## Context Managers for Resources (SDK)

The SDK encourages context managers for both the client and streaming responses, ensuring proper cleanup of httpx connections. [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

```python
with OpenAI() as client:
    with client.chat.completions.create(stream=True, ...) as stream:
        for chunk in stream:
            ...
```

## Register-at-Import Pattern (gym)

Gym environments register as side effects of module import. `gym/__init__.py` imports registration modules that call `gym.register()` at module scope, enabling `gym.make("CartPole-v1")` without users knowing which module contains the environment. This pattern was widely adopted by downstream RL libraries. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
# gym/envs/__init__.py
register(
    id="CartPole-v1",
    entry_point="gym.envs.classic_control:CartPoleEnv",
    max_episode_steps=500,
)
```

## Iterator Protocol (SDK + tiktoken)

Both the SDK and tiktoken make heavy use of Python's iterator protocol. SDK streaming returns `Stream[T]` implementing `__iter__` and `__next__` with `close()` for early termination. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```python
class Stream(Generic[T]):
    def __iter__(self) -> Iterator[T]:
        return self
    def __next__(self) -> T:
        ...
    def close(self) -> None:
        ...
```

## argparse CLI Entry Points (Research)

Research repos expose CLIs via argparse in `__main__.py` or console script entry points. No click, no typer, no rich — argparse is sufficient for research CLIs. [c8b1d43](https://github.com/openai/whisper/commit/c8b1d43)

```python
# whisper/transcribe.py
def cli():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("audio", nargs="+", type=str)
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", type=str, default=None)
    ...

# setup.py
entry_points={"console_scripts": ["whisper=whisper.transcribe:cli"]},
```

## Python 3.7+ Baseline

The SDK declares `requires-python = ">=3.7.1"` and avoids newer features: no walrus operator, no `match/case`, no `X | Y` union syntax. `typing_extensions` backports `Literal`, `TypedDict`, and `Required` to 3.7. Research code is less strict — Whisper effectively requires 3.8+. [f8a2c64](https://github.com/openai/openai-python/commit/f8a2c64)
