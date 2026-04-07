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

Functions rarely have docstrings. Instead, critical lines get inline comments explaining _why_ or _what_ in plain English. The comment density is high in numerical code and low in boilerplate. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

```python
def forward(self, idx, targets=None):
    b, t = idx.size()
    assert t <= self.config.block_size, f"Cannot forward, model block size is {self.config.block_size}"
    pos = torch.arange(0, t, dtype=torch.long, device=device)  # shape (t)

    # forward the GPT model itself
    tok_emb = self.transformer.wte(idx)  # token embeddings of shape (b, t, n_embd)
    pos_emb = self.transformer.wpe(pos)  # position embeddings of shape (1, t, n_embd)
    x = self.transformer.drop(tok_emb + pos_emb)
    for block in self.transformer.h:
        x = block(x)
    x = self.transformer.ln_f(x)
```

The pattern: no function-level docstring, but shape annotations and "forward the GPT model itself" section headers inline. This treats the code itself as the documentation.

## Section Headers in Code

Long functions use comment lines as section dividers: `# --- forward pass ---`, `# --- loss ---`, `# --- backward pass ---`. These create a visual table of contents when scrolling through a file. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

In `llm.c`, the equivalent is C-style block comments:

```c
// ----------------------------------------------------------------------------
// GPT-2 model definition
// ----------------------------------------------------------------------------
```

These dividers appear at major section boundaries — type definitions, forward pass functions, backward pass functions, training loop. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

## Paper References

Comments frequently cite the original papers. "Attention Is All You Need", "Language Models are Unsupervised Multitask Learners" (GPT-2 paper), and specific equations are referenced by section number. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
# causal self-attention; Self-attend: (B, nh, T, hs) x (B, nh, hs, T) -> (B, nh, T, T)
# efficient attention using Flash Attention CUDA kernels
att = F.scaled_dot_product_attention(q, k, v, attn_mask=None, dropout_p=self.dropout)
```

## README as Primary Documentation

Each repository's `README.md` is the main documentation artifact. READMEs include: what the project is, how to install/run it, expected output, and architectural overview. There are no separate docs sites, no Sphinx, no generated API docs. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

The README for nanoGPT runs to ~500 lines and includes performance benchmarks, configuration examples, and links to explanatory YouTube videos. It is the sole entry point for new users.

## Pedagogical Tone

Comments are written in first person and speak directly to the reader: "we need to be careful here", "note that this is different from", "the key insight is that." This is consistent with the educational framing — the code is a teaching artifact, and comments are the lecture. [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

```python
# this is the key operation of the entire autograd engine.
# during the forward pass we just do the operation.
# the _backward closure will be called during backpropagation.
```

## No Generated Documentation

There are no auto-generated docs, type stubs, or API reference pages. `help(GPT)` would return nothing useful. The documentation _is_ the source code plus the README. This is a deliberate choice for educational repositories where the goal is reading the code, not calling an API.
