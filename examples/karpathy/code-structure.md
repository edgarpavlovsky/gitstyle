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

The defining structural choice across Karpathy's work is radical flatness. Core implementations live in a single file — `micrograd/engine.py` (150 lines), `minbpe/basic.py` (200 lines), `nanoGPT/model.py` (300 lines), `llm.c/train_gpt2.c` (~2000 lines). The entire autograd engine, tokenizer, or transformer fits in one reading session. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

This serves the pedagogical mission directly: splitting code across modules forces the reader to hold a mental import graph, which competes with the cognitive budget they need for understanding the algorithm itself. A single file means a single linear path from "what is this?" to "I understand it." Compare this to production ML codebases like Hugging Face Transformers, where the GPT-2 implementation spans a dozen files across modeling, configuration, and tokenization modules. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

The single-file philosophy scales remarkably far. `micrograd/engine.py` at 150 lines and `llm.c/train_gpt2.c` at ~2000 lines are both single-file designs, but they solve for different constraints — one for minimal conceptual footprint, the other for keeping the entire GPT-2 forward/backward pass traceable without jumping between compilation units.

## Top-to-Bottom Readability

Files are structured to be read linearly, like a paper. Imports come first, then configuration, then helper functions, then the main class or training loop, then `if __name__ == "__main__"` at the bottom. Each function is defined before it is used — no forward references, no "scroll up to find the definition." [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
# typical file structure in micrograd/engine.py
class Value:
    """stores a single scalar value and its gradient"""

    def __init__(self, data, _children=(), _op=''):
        self.data = data
        self.grad = 0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __add__(self, other): ...
    def __mul__(self, other): ...
    def backward(self): ...
```

The ordering within a class follows the same principle: `__init__`, then operators, then the core method (`backward`). The reader never needs to jump around.

## No Package Hierarchy

Projects are not structured as installable packages with `setup.py` or deep `src/` layouts. The root directory _is_ the project. `nanoGPT/` contains `model.py`, `train.py`, `sample.py`, `configurator.py`, and data preparation scripts — all siblings at the top level. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

`llm.c` follows the same pattern in C: `train_gpt2.c`, `test_gpt2.c`, and utility files all live in the project root. No `src/` directory, no `include/` directory. See [[languages/c]] for C-specific conventions. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

This flat layout eliminates a class of questions: there is no `__init__.py` to inspect, no relative import confusion, no package path to configure. `python train.py` works from the repo root.

## Data Alongside Code

Data preparation scripts and small datasets live in the same repository, typically under a `data/` directory. `nanoGPT/data/shakespeare_char/` contains both the preparation script (`prepare.py`) and the generated binary files. This makes the project fully self-contained — clone and run, with no external data pipeline to set up. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)

## File Size Budget

No single Python file exceeds ~400 lines. When `train.py` in nanoGPT approached 350 lines, configuration handling was extracted to `configurator.py` (40 lines) rather than letting the file grow unbounded. The budget is "one file = one concept that fits in your head." [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

The C code in `llm.c` breaks this budget by necessity — a single translation unit for GPT-2 training requires thousands of lines because C lacks the abstraction density of Python. The compensating strategy is aggressive use of section-header comments (see [[comments-and-docs]]) to create navigable regions within the large file.

## Clone-and-Run Self-Containment

Every project is designed so that `git clone` + one command produces a working result. nanoGPT includes data preparation scripts. micrograd needs nothing beyond Python itself. `llm.c` needs only `gcc`. This self-containment is a structural decision, not just convenience — it means the reader never encounters a broken setup step that derails their learning before they see a single line of the algorithm. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)
