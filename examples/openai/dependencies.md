---
title: "Dependencies"
category: style
confidence: high
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym, openai/triton]
related: [code-structure, patterns, type-discipline]
last_updated: 2026-04-07
---

# Dependencies

## SDK: httpx as the HTTP Client

The Python SDK uses httpx as its HTTP client — not requests, not aiohttp, not urllib3 directly. httpx provides both sync and async interfaces from a single library, which aligns with the SDK's mirrored sync/async architecture. The switch from requests to httpx happened during the v1.0 rewrite when the SDK moved to Stainless generation. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```python
# _base_client.py
import httpx

class SyncAPIClient:
    _client: httpx.Client

    def __init__(self, ...):
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            follow_redirects=True,
        )
```

httpx also enables the SDK's streaming implementation — `httpx.Response.iter_bytes()` provides the raw byte stream for SSE parsing. See [[patterns]] for the streaming pattern.

## SDK: Pydantic for Response Modeling

Pydantic v2 is the response modeling layer in openai-python. Every API response type inherits from `pydantic.BaseModel`. The SDK uses Pydantic's `model_validate` for deserialization and leverages its JSON schema generation for documentation. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

```python
from pydantic import BaseModel

class ChatCompletion(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    ...
```

The dependency on Pydantic v2 (not v1) is pinned. The SDK includes compatibility handling for users still on Pydantic v1 but encourages migration.

## SDK: anyio for Async Abstraction

The Python SDK uses anyio for async support, allowing compatibility with both asyncio and trio event loops. This is a Stainless convention — their generated SDKs abstract over the async runtime rather than hardcoding asyncio. [c2e9a47](https://github.com/openai/openai-python/commit/c2e9a47)

```python
import anyio

async def _sleep(self, seconds: float) -> None:
    await anyio.sleep(seconds)
```

In practice, nearly all users run on asyncio, but anyio support costs little and enables trio compatibility for users who need it.

## Node SDK: node-fetch and FormData

openai-node uses `node-fetch` for HTTP in Node.js environments and the native `fetch` in edge/browser environments. Form data uploads (for audio transcription, file uploads) use the `formdata-node` package. The SDK also bundles a custom SSE parser. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

## Research Code: PyTorch as the Only Framework

Across whisper, CLIP, and gym's neural network components, PyTorch is the sole deep learning framework. There is no TensorFlow, no JAX, no framework-agnostic abstraction layer. PyTorch is used directly — `torch.nn`, `torch.optim`, `torch.nn.functional` — without training frameworks like Lightning or Accelerate. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

```python
# whisper/model.py — direct PyTorch, no wrappers
import torch
import torch.nn.functional as F
from torch import Tensor, nn
```

This is consistent across the research repos and reflects OpenAI's historical commitment to PyTorch for all public research code.

## tiktoken: Rust via PyO3/maturin

tiktoken's performance-critical BPE implementation is written in Rust and compiled to a Python extension via PyO3 and maturin. The build system is maturin, configured in `pyproject.toml`. This produces a `_tiktoken.so` that the Python package imports. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```toml
# pyproject.toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[tool.maturin]
bindings = "pyo3"
```

The choice of Rust over C/C++ for the performance core is notable — tiktoken was one of the earlier high-profile Python packages to adopt the Rust+PyO3 pattern. The `regex` crate handles the pre-tokenization regex, and `rustc-hash` provides the fast hash map for BPE lookups.

## tiktoken: requests for BPE Rank Downloads

tiktoken uses the `requests` library (not httpx) for downloading BPE rank files from OpenAI's blob storage. The ranks are cached locally after first download. This is the one place in the org where `requests` appears in active code — the SDK exclusively uses httpx. [b7c1d43](https://github.com/openai/tiktoken/commit/b7c1d43)

## Triton: LLVM/MLIR Compiler Stack

Triton depends on the LLVM/MLIR compiler infrastructure for code generation. The C++ backend links against LLVM libraries, and the Python frontend uses pybind11 (not PyO3) for the C++/Python boundary. Third-party CUDA and ROCm SDKs are build-time dependencies for GPU backend support. [b3d7e14](https://github.com/openai/triton/commit/b3d7e14)

## Build Tools: pyproject.toml Over setup.py

The organization is migrating toward `pyproject.toml` as the standard build configuration. The SDKs and tiktoken use `pyproject.toml` with Hatch (SDKs) or maturin (tiktoken) as build backends. Older research repos like whisper and CLIP still use `setup.py` with setuptools. Gym used `setup.py` throughout its lifetime. [c8b1d43](https://github.com/openai/openai-python/commit/c8b1d43)

```toml
# openai-python pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "openai"
requires-python = ">=3.7.1"
dependencies = [
    "httpx>=0.23.0,<1",
    "pydantic>=1.9.0,<3",
    "typing-extensions>=4.7,<5",
    "anyio>=3.5.0,<5",
    "distro>=1.7.0,<2",
    "sniffio",
]
```

## Dependency Pinning: Ranges in Libraries, Exact in Apps

OpenAI libraries specify dependency ranges (`httpx>=0.23.0,<1`) rather than exact pins. This gives downstream consumers flexibility. Lock files (`poetry.lock`, `package-lock.json`) exist in SDK repos for CI reproducibility but are not shipped with the package. [f8a2c64](https://github.com/openai/openai-python/commit/f8a2c64)

## No Monorepo Tooling

Each repository is a standalone project with its own dependencies and build configuration. There is no monorepo tooling (no Nx, no Turborepo, no Bazel). The SDKs, research code, and tooling libraries are fully independent packages. The only cross-repo dependency is that whisper and the cookbook depend on `tiktoken` and `openai` as PyPI packages.

## Linting and Formatting: Ruff for Python

The Python SDK uses Ruff for both linting and formatting, replacing the earlier combination of black + isort + flake8. Research repos are less consistent — whisper uses black for formatting, CLIP has no configured formatter. [e8b3c19](https://github.com/openai/openai-python/commit/e8b3c19)

```toml
# pyproject.toml (SDK)
[tool.ruff]
line-length = 120
target-version = "py37"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]
```
