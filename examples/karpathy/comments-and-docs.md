---
title: "Comments & Documentation"
category: style
confidence: high
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe, karpathy/makemore]
related: [naming-conventions, type-discipline, code-structure]
last_updated: 2026-04-07
---

# Comments & Documentation

## Inline Explanations Over Docstrings

Functions rarely have docstrings. Instead, critical lines get inline comments explaining _why_ or _what_ in plain English. The comment density is high in numerical code and low in boilerplate — comments appear where the algorithm is non-obvious, not where the syntax already tells the story. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
# from micrograd/engine.py — comments explain the calculus, not the Python
def __mul__(self, other):
    other = other if isinstance(other, Value) else Value(other)
    out = Value(self.data * other.data, (self, other), '*')
    def _backward():
        self.grad += other.data * out.grad   # chain rule: d(a*b)/da = b
        other.grad += self.data * out.grad   # chain rule: d(a*b)/db = a
    out._backward = _backward
    return out
```

The pattern: no function-level docstring, but inline annotations at the points where the reader needs help. This treats the code as the primary documentation and comments as margin notes.

## Section Headers in Code

Long functions use comment lines as section dividers: `# --- forward pass ---`, `# --- loss ---`, `# --- backward pass ---`. These create a visual table of contents when scrolling through a file. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

In `llm.c`, the equivalent is C-style block comments that span the full line:

```c
// ----------------------------------------------------------------------------
// GPT-2 model definition
// ----------------------------------------------------------------------------
```

These dividers appear at major section boundaries — type definitions, forward pass functions, backward pass functions, training loop. They compensate for the single-file structure (see [[code-structure]]): without module boundaries, section headers are the only navigational aid. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

## Paper References

Comments frequently cite the original papers. "Attention Is All You Need", "Language Models are Unsupervised Multitask Learners" (GPT-2 paper), and specific equations are referenced by section number. This turns the code into an annotated bibliography — the reader can look up exactly which paper section a line of code implements. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
# causal self-attention; Self-attend: (B, nh, T, hs) x (B, nh, hs, T) -> (B, nh, T, T)
# efficient attention using Flash Attention CUDA kernels
att = F.scaled_dot_product_attention(q, k, v, attn_mask=None, dropout_p=self.dropout)
```

## README as Primary Documentation

Each repository's `README.md` is the sole documentation artifact. READMEs include: what the project is, how to install/run it, expected output, and architectural overview. There are no separate docs sites, no Sphinx, no generated API docs. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

The README for nanoGPT runs to ~500 lines and includes performance benchmarks, configuration examples, and links to explanatory YouTube videos. It functions as textbook, API reference, and getting-started guide in one file. The README for micrograd is shorter but follows the same structure: diagram, explanation, quickstart.

## Pedagogical Tone

Comments are written in first person and speak directly to the reader: "we need to be careful here", "note that this is different from", "the key insight is that." The code is a teaching artifact, and comments are the lecture. [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

```python
# this is the key operation of the entire autograd engine.
# during the forward pass we just do the operation.
# the _backward closure will be called during backpropagation.
```

This tone is consistent across all repositories and distinguishes Karpathy's code from typical open-source projects, where comments explain _what_ for maintainers rather than _why_ for learners.

## No Generated Documentation

There are no auto-generated docs, type stubs, or API reference pages. `help(GPT)` would return nothing useful. The documentation _is_ the source code plus the README. For educational repositories where the goal is reading the code, not calling an API, this is the correct tradeoff — generated docs would create the illusion that the code is a library to be consumed, when it is actually a text to be studied.

## Comment Density Scales With Algorithmic Density

Comment density is not uniform — it correlates with algorithmic complexity. The attention mechanism in nanoGPT has a comment on nearly every line explaining the shape transformations. The boilerplate `__init__` methods that wire up `nn.Module` layers have no comments at all. In `llm.c`, the backward pass functions are more heavily commented than the forward pass, because the gradient computations are less intuitive. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

This selective density is a sign of expert commenting: annotations appear where the reader's mental model is most likely to diverge from what the code does, not where the code is longest.
