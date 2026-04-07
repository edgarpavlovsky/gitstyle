---
title: "Code Structure"
category: style
confidence: high
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe, karpathy/makemore]
related: [naming-conventions, patterns, dependencies]
last_updated: 2026-04-07
---

# Code Structure

## Single-File Implementations

The defining structural choice across Karpathy's work is radical flatness. Core implementations live in a single file — `micrograd/engine.py` (150 lines), `minbpe/base.py` + `minbpe/basic.py` (200 lines each), `nanoGPT/model.py` (300 lines). The entire autograd engine, tokenizer, or transformer fits in one scroll session. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

This is not accidental. Commit messages explicitly frame single-file design as a pedagogical goal: "the whole thing should be readable in one sitting." When nanoGPT's `train.py` grew past 300 lines, the response was not to split into modules but to simplify the training loop. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

## Top-to-Bottom Readability

Files are structured to be read linearly. Imports come first, then data classes or config, then helper functions, then the main class or training loop, then `if __name__ == "__main__"` at the bottom. There is no forward-reference problem because each function is defined before it is used. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
# typical file structure in nanoGPT/model.py
import math
import torch
import torch.nn as nn

# --- config ---
@dataclass
class GPTConfig:
    block_size: int = 1024
    vocab_size: int = 50257
    n_layer: int = 12
    ...

# --- building blocks ---
class CausalSelfAttention(nn.Module): ...
class MLP(nn.Module): ...
class Block(nn.Module): ...

# --- main model ---
class GPT(nn.Module): ...
```

## No Package Hierarchy

Projects are not structured as installable packages with `setup.py` or deep `src/` layouts. The root directory _is_ the project. `nanoGPT/` contains `model.py`, `train.py`, `sample.py`, `configurator.py`, and data preparation scripts — all siblings at the top level. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

`llm.c` follows the same pattern in C: `train_gpt2.c`, `test_gpt2.c`, and utility files all live in the project root. No `src/` directory, no `include/` directory. See [[languages/c]] for C-specific conventions. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

## Data Alongside Code

Data preparation scripts and small datasets live in the same repository, typically under a `data/` directory. `nanoGPT/data/shakespeare_char/` contains both the preparation script (`prepare.py`) and the generated binary files. This makes the project fully self-contained — clone and run. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)

## File Size Budget

No single file exceeds ~400 lines. When `train.py` in nanoGPT approached 350 lines, configuration handling was extracted to `configurator.py` (40 lines) rather than letting the file grow unbounded. The budget appears to be "one file = one concept that fits in your head." [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)
