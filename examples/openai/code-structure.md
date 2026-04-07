---
title: "Code Structure"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym, openai/triton]
related: [naming-conventions, patterns, dependencies]
last_updated: 2026-04-07
---

# Code Structure

## SDK: Resource-Based Module Hierarchy

The Python and Node SDKs follow a resource-based architecture directly influenced by Stripe's API client design. Each API resource (completions, embeddings, files, fine-tuning) maps to its own module under a `resources/` directory. This pattern was established when OpenAI adopted Stainless for SDK generation. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```
openai-python/
  src/openai/
    resources/
      chat/
        completions.py
        __init__.py
      embeddings.py
      files.py
      fine_tuning/
        jobs.py
        __init__.py
      audio/
        transcriptions.py
        translations.py
      images.py
      models.py
      moderations.py
    types/
      chat/
        chat_completion.py
        chat_completion_chunk.py
      embedding.py
      file_object.py
    _client.py
    _streaming.py
    _response.py
```

Each resource module exports a single class (e.g., `Completions`, `AsyncCompletions`) that encapsulates all HTTP methods for that resource. The `types/` directory mirrors the `resources/` structure with Pydantic models for every request and response shape. [b8c4d19](https://github.com/openai/openai-python/commit/b8c4d19)

## SDK: Mirrored Sync/Async Architecture

Across both openai-python and openai-node, every resource class exists in two forms: synchronous and asynchronous. The file structure does not separate these into different directories — both live in the same module. The async variant inherits from `AsyncAPIResource` and has method signatures that return awaitables. [c2e9a47](https://github.com/openai/openai-python/commit/c2e9a47)

```python
# resources/chat/completions.py contains both:
class Completions(SyncAPIResource):
    def create(self, *, messages, model, **kwargs) -> ChatCompletion: ...

class AsyncCompletions(AsyncAPIResource):
    async def create(self, *, messages, model, **kwargs) -> ChatCompletion: ...
```

This convention is consistent across the organization — openai-node follows the identical pattern with `Completions` and `AsyncCompletions` in the same file.

## Research Code: Flat Module Layout

Research repositories use dramatically flatter structures. Whisper places all core logic under `whisper/` with a handful of modules: `model.py`, `audio.py`, `decoding.py`, `tokenizer.py`, `transcribe.py`. No `resources/`, no `types/`, no nested hierarchies. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```
whisper/
  whisper/
    model.py
    audio.py
    decoding.py
    tokenizer.py
    transcribe.py
    __init__.py
    assets/
      mel_filters.npz
      multilingual.tiktoken
  setup.py
```

CLIP follows the same pattern — `clip/model.py`, `clip/clip.py`, `clip/simple_tokenizer.py`. The entire model definition and inference pipeline fit in 3-4 files. [e7f2c83](https://github.com/openai/CLIP/commit/e7f2c83)

## gym: Interface-Centric Package Design

OpenAI Gym established a distinct structural pattern centered on abstract interfaces. The `gym/core.py` file defines the `Env` base class with `step()`, `reset()`, `render()`, and `close()` methods. Individual environments are registered as entry points rather than imported directly. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

```
gym/
  gym/
    core.py          # Env, Wrapper, ObservationWrapper, etc.
    spaces/          # Box, Discrete, MultiBinary, etc.
    envs/
      classic_control/
      box2d/
      mujoco/
    wrappers/
    utils/
    envs/registration.py
```

This plugin-style architecture — define an interface, register implementations — is unique to gym within the OpenAI org and was influential in the broader ML ecosystem.

## tiktoken: Rust Core with Python Shell

tiktoken exemplifies the hybrid performance pattern: a Rust core compiled via PyO3/maturin, wrapped in a thin Python API. The directory structure reflects this split. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```
tiktoken/
  src/lib.rs           # Rust BPE implementation
  tiktoken/
    _educational.py    # Pure-Python reference impl for learning
    core.py            # Python API wrapping Rust
    model.py           # Model-to-encoding registry
    load.py            # BPE rank file loading
  Cargo.toml
  pyproject.toml
```

The Rust source lives at the project root under `src/`, while the Python package occupies `tiktoken/`. The `_educational.py` module is notable — a pure-Python BPE implementation included explicitly for readability, not performance. See [[dependencies]] for more on the Rust/Python boundary.

## Triton: Compiler Infrastructure Layout

Triton follows C++ compiler project conventions with `lib/`, `include/`, and `python/` top-level directories. The Python DSL frontend lives under `python/triton/`, while the MLIR-based compiler backend lives in `lib/` and `include/`. [b3d7e14](https://github.com/openai/triton/commit/b3d7e14)

```
triton/
  include/triton/
    Dialect/
    Conversion/
    Analysis/
  lib/
    Dialect/
    Conversion/
    Analysis/
  python/
    triton/
      language/
      compiler/
      runtime/
  third_party/
```

This is the most complex directory structure in the org, reflecting Triton's dual nature as both a Python DSL and an LLVM/MLIR compiler.

## Installable Packages as the Default

Unlike many research orgs, OpenAI repositories are almost universally structured as installable Python packages. Whisper, CLIP, tiktoken, and gym all have `setup.py` or `pyproject.toml`. The SDKs use `pyproject.toml` with Hatch as the build system. Research repos tend toward `setup.py` with setuptools. [c8b1d43](https://github.com/openai/whisper/commit/c8b1d43)

```bash
# every major repo supports:
pip install openai
pip install openai-whisper
pip install tiktoken
pip install gym
```

This "pip-installable by default" convention makes OpenAI's code immediately usable without cloning or path manipulation. See [[dependencies]] for build tool choices.
