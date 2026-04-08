---
title: Python Style Guide
category: language
confidence: 0.88
source_repos:
  - karpathy/EigenLibSVM
  - karpathy/KarpathyTalk
  - karpathy/LLM101n
  - karpathy/Random-Forest-Matlab
  - karpathy/arxiv-sanity-lite
  - karpathy/arxiv-sanity-preserver
  - karpathy/autoresearch
  - karpathy/build-nanogpt
  - karpathy/calorie
  - karpathy/char-rnn
  - karpathy/convnetjs
  - karpathy/covid-sanity
  - karpathy/cryptos
  - karpathy/deep-vector-quantization
  - karpathy/find-birds
  - karpathy/forestjs
  - karpathy/hn-time-capsule
  - karpathy/jobs
  - karpathy/karpathy
  - karpathy/karpathy.github.io
  - karpathy/lecun1989-repro
  - karpathy/llama2.c
  - karpathy/llm-council
  - karpathy/llm.c
  - karpathy/makemore
  - karpathy/micrograd
  - karpathy/minGPT
  - karpathy/minbpe
  - karpathy/nanoGPT
  - karpathy/nanochat
  - karpathy/neuraltalk
  - karpathy/neuraltalk2
  - karpathy/ng-video-lecture
  - karpathy/nipspreview
  - karpathy/nn-zero-to-hero
  - karpathy/notpygamejs
  - karpathy/paper-notes
  - karpathy/pytorch-normalizing-flows
  - karpathy/randomfun
  - karpathy/reader3
  - karpathy/recurrentjs
  - karpathy/reinforcejs
  - karpathy/rendergit
  - karpathy/researchlei
  - karpathy/researchpooler
  - karpathy/rustbpe
  - karpathy/scholaroctopus
  - karpathy/svmjs
  - karpathy/tf-agent
  - karpathy/tsnejs
  - karpathy/twoolpy
  - karpathy/ulogme
last_updated: 2026-04-08
---
# Python Style Guide

This developer demonstrates mastery of Python's idiomatic patterns and modern features, with a strong focus on scientific computing and deep learning frameworks.

## Modern Python Features

The developer consistently leverages modern Python [[language-idioms]], including:

- **Type annotations and dataclasses**: Uses `@dataclass` decorators with field defaults and type hints throughout (64960f99)
- **F-strings for formatting**: Prefers f-strings over older formatting methods, even using numeric underscores like `1_000_000` for readability (7fa0be64)
- **Context managers**: Employs `with` statements and `nullcontext` appropriately (6e6a5281, a022d02e)
- **Pathlib for file operations**: Uses `pathlib` instead of `os.path` for modern file handling (e9345a4b, 739f1013)

## Functional Programming Patterns

The developer embraces Python's functional programming capabilities:

- **List and dictionary comprehensions**: Uses comprehensions extensively for data transformations rather than explicit loops (f99b57a9, 12ccb4ab, 6e85778b)
- **Generator expressions**: Employs generators for memory-efficient operations (7e8c3cd0, 9fd9cc02)
- **Lambda functions**: Uses inline lambdas for initialization logic and sorting operations (a1e226dd, 51c54e0f)
- **Decorators**: Applies `@lru_cache`, `@classmethod`, and `@staticmethod` appropriately (64960f99, 0a20bbc1)

## Scientific Computing Idioms

Strong command of NumPy and scientific Python [[patterns]]:

- **NumPy broadcasting**: Leverages vectorized operations and broadcasting instead of explicit loops (2c99eac2, f399811c)
- **Array operations**: Uses NumPy idiomatically for numerical computations (4c84bc74, 9740a652)
- **Matplotlib integration**: Consistently uses `%matplotlib inline` in notebooks (26675947, 2fb6f76d)

## PyTorch-Specific Patterns

The developer demonstrates deep familiarity with PyTorch [[language-idioms]]:

- **Device-agnostic code**: Writes portable code with explicit device type checking for CUDA operations (6104ab1b, 41af0d18)
- **Module patterns**: Uses `nn.Module` inheritance, `ModuleList`, and `ModuleDict` correctly (a6e0bee4, b60e119b)
- **Custom autograd functions**: Implements PyTorch-specific patterns for distributed training (e569b59f, 1076f970)
- **Parameter management**: Uses `nn.Parameter` explicitly rather than relying on higher-level abstractions (a1e226dd, ac30aa07)

## Async/Await Patterns

The developer uses Python's async features idiomatically:

- Implements `async`/`await` patterns throughout asynchronous code (eb0eb26f, 87b4a178)
- Leverages `asyncio` for concurrent operations following modern async conventions

## Code Organization

Follows Python conventions for [[code-structure]]:

- **Main guards**: Consistently uses `if __name__ == '__main__':` guards (4eb7a96b, 02511eba)
- **Public API declarations**: Uses `__all__` to define public interfaces (436af545)
- **Future annotations**: Imports `from __future__ import annotations` for forward compatibility (e661637e)

## Legacy Code Handling

The codebase shows evolution from Python 2.x to 3.x:

- Older commits use Python 2 syntax like `print` statements and `cPickle` (72204877, f85afab4)
- Modern commits fully embrace Python 3 features and idioms

## Platform Compatibility

Handles cross-platform concerns directly:

- Uses `sys.platform` conditionals for platform-specific behavior rather than abstraction libraries (d4798e3b)
- Writes device-agnostic PyTorch code for CPU/GPU compatibility

## Educational Clarity

When writing educational code, the developer prioritizes clarity:

- Removes unnecessary complexity like weight initialization and gradient clipping for teaching purposes (d26d9750, 4e0137dd)
- Maintains readable, straightforward implementations over premature optimization

This developer's Python style reflects deep language expertise, embracing both modern features and domain-specific patterns while maintaining code clarity and idiomatic correctness.
