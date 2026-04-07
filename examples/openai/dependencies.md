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

The Python SDK uses httpx — not requests, not aiohttp. httpx provides both sync and async interfaces from a single library, aligning with the SDK's mirrored sync/async architecture. The switch from requests happened during the v1.0 Stainless rewrite. httpx also enables streaming via `iter_bytes()` for SSE parsing. See [[patterns]]. [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

## SDK: Pydantic v2 for Response Modeling

Every API response type inherits from `pydantic.BaseModel`. The SDK uses `model_validate` for deserialization and leverages Pydantic's JSON schema generation. The Pydantic v2 dependency is pinned, with compatibility handling for users still on v1. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)

## SDK: anyio for Async Abstraction

The Python SDK uses anyio for async support, enabling compatibility with both asyncio and trio. This is a Stainless convention — their generated SDKs abstract over the async runtime. In practice nearly all users run asyncio, but anyio costs little. [c2e9a47](https://github.com/openai/openai-python/commit/c2e9a47)

## Node SDK: node-fetch and Native fetch

openai-node uses `node-fetch` in Node.js and native `fetch` in edge/browser environments. File uploads use `formdata-node`. The SDK bundles a custom SSE parser. [e1c8a37](https://github.com/openai/openai-node/commit/e1c8a37)

## Research Code: PyTorch as the Only Framework

Across Whisper, CLIP, and gym's neural network components, PyTorch is the sole deep learning framework. No TensorFlow, no JAX, no framework-agnostic abstraction. PyTorch is used directly — `torch.nn`, `torch.optim`, `torch.nn.functional` — without Lightning or Accelerate wrappers. This reflects OpenAI's historical commitment to PyTorch for all public research code. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

## tiktoken: Rust via PyO3/maturin

tiktoken's BPE core is Rust compiled to a Python extension via PyO3 and maturin. This was one of the earlier high-profile Python packages to adopt the Rust+PyO3 pattern. The `regex` crate handles pre-tokenization, and `rustc-hash` provides fast hash maps for BPE lookups. [a4e2f91](https://github.com/openai/tiktoken/commit/a4e2f91)

```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[tool.maturin]
bindings = "pyo3"
```

## tiktoken: requests for BPE Rank Downloads

tiktoken uses `requests` (not httpx) for downloading BPE rank files from blob storage, cached locally after first download. This is the one place in the org where `requests` appears in active code. [b7c1d43](https://github.com/openai/tiktoken/commit/b7c1d43)

## Triton: LLVM/MLIR Compiler Stack

Triton depends on LLVM/MLIR for code generation — a completely different dependency universe from the rest of the org. The C++ backend links against LLVM libraries; the Python frontend uses pybind11 (not PyO3) for the C++/Python boundary. CUDA and ROCm SDKs are build-time dependencies. There is zero overlap between Triton's dependency tree and any other OpenAI repository. Even the FFI choice differs: tiktoken uses PyO3, Triton uses pybind11. [b3d7e14](https://github.com/openai/triton/commit/b3d7e14)

## Build Tools: pyproject.toml over setup.py

The org is migrating toward `pyproject.toml`. SDKs use Hatch; tiktoken uses maturin. Older research repos (Whisper, CLIP, gym) still use `setup.py` with setuptools. [c8b1d43](https://github.com/openai/openai-python/commit/c8b1d43)

```toml
# openai-python pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "openai"
dependencies = [
    "httpx>=0.23.0,<1",
    "pydantic>=1.9.0,<3",
    "typing-extensions>=4.7,<5",
    "anyio>=3.5.0,<5",
    "distro>=1.7.0,<2",
    "sniffio",
]
```

## Dependency Pinning: Ranges in Libraries

Libraries specify dependency ranges (`httpx>=0.23.0,<1`) for downstream flexibility. Lock files exist in SDK repos for CI reproducibility but are not shipped. [f8a2c64](https://github.com/openai/openai-python/commit/f8a2c64)

## No Monorepo Tooling

Each repository is standalone — no Nx, no Turborepo, no Bazel. The only cross-repo dependency is that Whisper and the cookbook depend on `tiktoken` and `openai` as PyPI packages. This independence is deliberate: it means each repo can be cloned, installed, and developed without any other OpenAI code.

## Linting: Ruff for Python

The SDK uses Ruff for linting and formatting, replacing black + isort + flake8. Research repos are less consistent — Whisper uses black, CLIP has no configured formatter. [e8b3c19](https://github.com/openai/openai-python/commit/e8b3c19)

```toml
[tool.ruff]
line-length = 120
target-version = "py37"

[tool.ruff.lint]
select = ["E", "F", "I", "W"]
```
