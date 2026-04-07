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

There are no utility libraries (no `tqdm`, no `rich`, no `click`), no configuration frameworks (no `hydra`, no `omegaconf`), no experiment tracking (no `wandb`, no `mlflow`). Every dependency that exists is load-bearing.

## PyTorch as the Only Framework

When a deep learning framework is needed, it is PyTorch. There is no TensorFlow, no JAX, no Flax in any repository. PyTorch is used directly — `torch.nn.Module`, `torch.optim`, `torch.nn.functional` — without wrappers like PyTorch Lightning or Hugging Face Accelerate. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
import torch
import torch.nn as nn
from torch.nn import functional as F

# that's it. no Lightning, no Accelerate, no deepspeed wrappers.
```

This is a conscious rejection of training frameworks. From a commit message: "complexity should be in understanding the model, not in understanding the framework." [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

## Zero External Dependencies in C

`llm.c` takes the no-dependency philosophy to its extreme. The entire GPT-2 training implementation uses only the C standard library — `stdio.h`, `stdlib.h`, `math.h`, `string.h`. No BLAS, no MKL, no external math library. Matrix multiplications are hand-written loops. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
// that's the entire dependency list
```

CUDA support was added later as an optional code path, but the CPU reference implementation remains dependency-free.

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

No `torch>=2.0.0,<2.1.0`. No lock files. The expectation is "latest stable works."

## Standard Library First

Python's standard library is preferred over third-party alternatives. File I/O uses `open()`, not `pathlib` (in most cases). Argument parsing uses `argparse` or raw `sys.argv` manipulation, not `click` or `typer`. JSON handling uses `json`, not `orjson`. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)

The exception is `tiktoken` (OpenAI's BPE library) which is used for tokenization in nanoGPT because writing a correct BPE tokenizer is a separate project — which Karpathy later did as `minbpe`.
