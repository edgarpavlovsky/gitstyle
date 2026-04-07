---
title: "Python Idioms"
category: language
confidence: high
sources: [openai/openai-python, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym, openai/openai-cookbook]
related: [naming-conventions, type-discipline, patterns, dependencies]
last_updated: 2026-04-07
---

# Python Idioms

## Two Dialects: SDK Python vs. Research Python

OpenAI's Python code exists in two distinct dialects. SDK Python is heavily typed, uses Pydantic models, async/await, and modern Python features (3.7+ baseline, increasingly 3.8+). Research Python is PyTorch-oriented, lightly typed, and optimized for readability by ML practitioners. Most idioms below note which dialect they belong to.

## Keyword-Only Parameters (SDK)

All SDK public methods use keyword-only arguments via the `*` separator. This is enforced by the Stainless generator and prevents positional-argument bugs in APIs with many optional parameters. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
def create(
    self,
    *,                          # everything after this is keyword-only
    messages: Iterable[ChatCompletionMessageParam],
    model: Union[str, ChatModel],
    frequency_penalty: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: Optional[bool] = None,
    temperature: Optional[float] = None,
) -> ChatCompletion:
```

## @overload for Type Narrowing (SDK)

The SDK uses `@typing.overload` extensively to provide precise return types based on argument values. The `stream` parameter is the canonical example — the overloads let type checkers know that `stream=True` returns `Stream[...]` and `stream=False` returns the concrete model. [c7a3e18](https://github.com/openai/openai-python/commit/c7a3e18)

```python
from typing import overload, Literal

@overload
def create(self, *, stream: Literal[False] = ..., **kwargs) -> ChatCompletion: ...
@overload
def create(self, *, stream: Literal[True], **kwargs) -> Stream[ChatCompletionChunk]: ...

def create(self, *, stream=False, **kwargs):
    ...
```

## __all__ for Public API Control (SDK)

SDK modules define `__all__` to control star imports and make the public API surface explicit. Internal modules (prefixed with `_`) are excluded from `__all__` in the package `__init__.py`. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

```python
# openai/__init__.py
__all__ = [
    "OpenAI",
    "AsyncOpenAI",
    "APIError",
    "APIConnectionError",
    "RateLimitError",
    ...
]
```

## Dataclass Configuration (Research)

Research repos use `@dataclass` for model configuration, mirroring the broader PyTorch community convention. Fields use type annotations and default values. No `attrs`, no Pydantic, no config files. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```python
@dataclass
class ModelDimensions:
    n_mels: int
    n_audio_ctx: int
    n_audio_state: int
    n_audio_head: int
    n_audio_layer: int
```

See [[type-discipline]] for the broader contrast between SDK and research typing approaches.

## torch.nn.functional Preference (Research)

Research code prefers the functional API (`F.gelu`, `F.softmax`, `F.cross_entropy`) for stateless operations. `nn.Module` subclasses are reserved for layers with learnable parameters. This is standard PyTorch convention and is consistent across whisper, CLIP, and gym. [e7f2c83](https://github.com/openai/whisper/commit/e7f2c83)

```python
import torch.nn.functional as F

# functional for activation, normalization without params
x = F.gelu(self.conv1(x))
x = F.layer_norm(x, normalized_shape)

# module for layers with weights
self.conv1 = nn.Conv1d(n_mels, n_state, kernel_size=3, padding=1)
```

## Context Managers for Resources (SDK)

The SDK encourages context manager usage for both the client and streaming responses. This ensures proper cleanup of httpx connections. [d2f1a93](https://github.com/openai/openai-python/commit/d2f1a93)

```python
# recommended pattern
with OpenAI() as client:
    with client.chat.completions.create(stream=True, ...) as stream:
        for chunk in stream:
            ...

# async equivalent
async with AsyncOpenAI() as client:
    async with await client.chat.completions.create(stream=True, ...) as stream:
        async for chunk in stream:
            ...
```

## Register-at-Import Pattern (gym)

Gym environments are registered as side effects of importing their modules. The `gym/__init__.py` imports environment registration modules, which call `gym.register()` at module scope. This lets `gym.make("CartPole-v1")` work without users needing to know which module contains the environment. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```python
# gym/envs/__init__.py
from gym.envs.registration import register

register(
    id="CartPole-v1",
    entry_point="gym.envs.classic_control:CartPoleEnv",
    max_episode_steps=500,
)
```

## Generator/Iterator Protocol (SDK + tiktoken)

Both the SDK and tiktoken make heavy use of Python's iterator protocol. SDK streaming returns `Stream[T]` which implements `__iter__` and `__next__`. tiktoken's encoding returns plain `list[int]` but uses generator patterns internally for batch encoding. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```python
# SDK Stream implements the iterator protocol
class Stream(Generic[T]):
    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        ...

    def close(self) -> None:
        ...
```

## argparse + CLI Entry Points (Research)

Research repos expose CLI interfaces via argparse in `__main__.py` or console script entry points. Whisper provides both: `whisper audio.mp3 --model large` works via a console script defined in `setup.py`. [c8b1d43](https://github.com/openai/whisper/commit/c8b1d43)

```python
# whisper/transcribe.py
def cli():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("audio", nargs="+", type=str, help="audio file(s) to transcribe")
    parser.add_argument("--model", default="small", help="name of the Whisper model to use")
    parser.add_argument("--language", type=str, default=None, help="language spoken in the audio")
    ...

# setup.py
entry_points={
    "console_scripts": ["whisper=whisper.transcribe:cli"],
},
```

No click, no typer, no rich — argparse is sufficient for research CLIs.

## Python 3.7+ Baseline

The SDK declares `requires-python = ">=3.7.1"` and avoids features newer than 3.7: no walrus operator, no `match/case`, no `X | Y` union syntax. `typing_extensions` backports newer typing features (`Literal`, `TypedDict`, `Required`) to 3.7. Research code is less strict — whisper effectively requires 3.8+ due to positional-only parameter syntax in dependencies. [f8a2c64](https://github.com/openai/openai-python/commit/f8a2c64)
