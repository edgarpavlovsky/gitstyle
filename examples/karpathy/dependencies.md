---
title: "Dependencies"
category: style
confidence: high
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe, karpathy/makemore]
related: [code-structure, patterns]
last_updated: 2026-04-07
---

# Dependencies

## Minimal Dependency Philosophy

The defining dependency pattern is radical minimalism. `micrograd` has zero dependencies — no numpy, no PyTorch, just Python's `math` module. `minbpe` depends only on `regex`. `nanoGPT` depends on `torch`, `numpy`, `tiktoken`, and `datasets` — the absolute minimum for training a transformer. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

There are no utility libraries (no `tqdm`, no `rich`, no `click`), no configuration frameworks (no `hydra`, no `omegaconf`), no experiment tracking (no `wandb`, no `mlflow`). Every dependency that exists is load-bearing — it does something that would take hundreds of lines to reimplement.

This minimalism serves the pedagogical mission: each dependency the reader does not have to understand is one fewer obstacle between them and the algorithm. A `tqdm` progress bar is convenient, but a `print(f"step {i}")` is transparent.

## PyTorch as the Only Framework

When a deep learning framework is needed, it is PyTorch. There is no TensorFlow, no JAX, no Flax in any repository. PyTorch is used directly — `torch.nn.Module`, `torch.optim`, `torch.nn.functional` — without wrappers like PyTorch Lightning or Hugging Face Accelerate. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
import torch
import torch.nn as nn
from torch.nn import functional as F

# that's it. no Lightning, no Accelerate, no deepspeed wrappers.
```

From a commit message: "complexity should be in understanding the model, not in understanding the framework." This rejects the trend toward training frameworks that manage distributed computing, mixed precision, and checkpointing behind an opaque API. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

## Zero External Dependencies in C

`llm.c` takes the no-dependency philosophy to its extreme. The entire GPT-2 training implementation uses only the C standard library — `stdio.h`, `stdlib.h`, `math.h`, `string.h`. No BLAS, no MKL, no external math library. Matrix multiplications are hand-written loops. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

This makes the build command `gcc train_gpt2.c -o train_gpt2 -lm` — no cmake, no pkg-config, no linker flags hunting for library paths. The reader goes from "I cloned this" to "I'm running GPT-2 training" in one compiler invocation. CUDA support was added later as an optional code path, but the CPU reference implementation remains dependency-free.

## No requirements.txt

Most repositories lack `requirements.txt` or `setup.py`. Dependencies are documented in the README: "install PyTorch, then run `python train.py`." The assumption is that users can install 2-3 well-known packages without automated dependency management. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

When `requirements.txt` does exist (as in nanoGPT), it lists 4-5 packages with no version pins:

```
torch
numpy
transformers
datasets
tiktoken
```

No `torch>=2.0.0,<2.1.0`. No lock files. The expectation is "latest stable works." This is the opposite of production dependency management, where pinning prevents environment drift. For educational code that someone runs once to learn from, the simplicity of unpinned deps outweighs the risk of version conflicts.

## Standard Library First

Python's standard library is preferred over third-party alternatives. File I/O uses `open()`, not `pathlib` (in most cases). Argument parsing uses `argparse` or raw `sys.argv` manipulation, not `click` or `typer`. JSON handling uses `json`, not `orjson`. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)

The exception is `tiktoken` (OpenAI's BPE library) which is used for tokenization in nanoGPT because writing a correct BPE tokenizer is a separate project — which Karpathy later did as `minbpe`. The dependency existed until the pedagogical itch demanded reimplementation.

## The Dependency Gradient

There is a clear gradient across the repositories: micrograd (zero deps) -> minbpe (`regex` only) -> nanoGPT (PyTorch + 4 packages) -> `llm.c` (zero deps, C standard library only). The gradient maps to pedagogical intent. micrograd and `llm.c` are "understand from scratch" projects where every line of computation is visible. nanoGPT accepts PyTorch as a given because the lesson is transformer architecture, not tensor computation. Each project's dependency set reveals what it considers prerequisite knowledge versus what it intends to teach.
