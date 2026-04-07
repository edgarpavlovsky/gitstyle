---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe, karpathy/makemore]
related: [code-structure, type-discipline, dependencies]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Rewrite-from-Scratch Over Abstraction

The dominant architectural pattern is reimplementation. Rather than wrapping existing libraries, Karpathy rewrites core algorithms from first principles: autograd in micrograd, BPE tokenization in minbpe, GPT-2 training in both Python (nanoGPT) and C (llm.c). The implementations are intentionally minimal — they reproduce the essential algorithm without the engineering overhead of production systems. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

This is a deliberate design philosophy. From a nanoGPT commit message: "the goal is not to compete with Hugging Face but to make GPT training understandable." [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

## Dataclass Configuration

Configuration is handled through Python dataclasses with sensible defaults. Every parameter has a default value, so the simplest possible invocation requires zero configuration. Overrides come from command-line arguments parsed into the dataclass, not from YAML/JSON config files. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
@dataclass
class GPTConfig:
    block_size: int = 1024
    vocab_size: int = 50304
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    dropout: float = 0.0
    bias: bool = True

# usage — override only what you need
config = GPTConfig(n_layer=6, n_head=6, n_embd=384)
```

There are no config files, no environment variable parsing, no config inheritance chains. The dataclass _is_ the documentation of available options. See [[dependencies]] for why external config libraries are avoided.

## Linear Training Loops

Training loops are flat, imperative `for` loops with no callback system, no trainer abstraction, no hooks. Everything happens in order: forward pass, loss computation, backward pass, optimizer step, logging. The entire training procedure is visible in 30 lines. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
for iter_num in range(max_iters):
    # evaluate the loss on train/val sets periodically
    if iter_num % eval_interval == 0:
        losses = estimate_loss()
        print(f"step {iter_num}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")

    # sample a batch of data
    xb, yb = get_batch('train')

    # forward, backward, update
    logits, loss = model(xb, yb)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()
```

No `Trainer.fit()`. No `on_epoch_end` callbacks. The training loop reads like pseudocode from a textbook.

## Operator Overloading for DSLs

In micrograd, Python's operator overloading creates a miniature autograd DSL. The `Value` class overloads `+`, `*`, `**`, `tanh`, etc., building a computation graph implicitly. This makes the neural network code look like pure math. [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

```python
# this builds a computation graph automatically
x = Value(2.0)
y = Value(-3.0)
z = x * y + Value(1.0)
z.backward()  # computes gradients through the graph
```

## Progressive Complexity

Repositories build from simple to complex. `makemore` starts with bigram models, progresses through MLPs, to RNNs, to transformers — each in its own notebook or script. Each version is self-contained and doesn't import from previous versions. The progression teaches concepts incrementally. [e3f8a4b](https://github.com/karpathy/makemore/commit/e3f8a4b)

## No Inheritance Hierarchies

Classes do not inherit from each other (beyond `nn.Module` which is framework-required). There are no abstract base classes, no mixins, no template method patterns. Each class is a concrete, standalone implementation. When two classes share logic, it is duplicated rather than extracted into a base class. [b7c1d5e](https://github.com/karpathy/minbpe/commit/b7c1d5e)

minbpe makes this explicit: `BasicTokenizer` and `RegexTokenizer` both inherit from `Tokenizer` (a thin base), but the base class is just a container for shared utility methods — `save`, `load`, `encode`. There is no abstract `merge` or `train` method — each subclass defines its own complete implementation.
