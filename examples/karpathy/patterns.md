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

From a nanoGPT commit message: "the goal is not to compete with Hugging Face but to make GPT training understandable." Each rewrite strips away exactly the layers that obscure the algorithm: Hugging Face's GPT-2 has generation strategies, model parallelism, and cache management; nanoGPT has the forward pass, the loss, and the backward pass. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

## Dataclass Configuration

Configuration is handled through Python dataclasses with sensible defaults. Every parameter has a default value, so the simplest possible invocation requires zero configuration. Overrides come from command-line arguments parsed into the dataclass, not from YAML/JSON config files. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

```python
# from nanoGPT configurator.py — override dataclass fields from command line
for key in globals():
    if key in config_keys:
        exec(f"{key} = {globals()[key]}")
```

There are no config files, no environment variable parsing, no config inheritance chains. The dataclass _is_ the documentation of available options. See [[dependencies]] for why external config libraries are avoided.

## Linear Training Loops

Training loops are flat, imperative `for` loops with no callback system, no trainer abstraction, no hooks. Everything happens in order: forward pass, loss computation, backward pass, optimizer step, logging. The entire training procedure is visible in 30 lines. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

```python
# from makemore — the same flat loop pattern at a smaller scale
for i in range(max_steps):
    # minibatch construct
    ix = torch.randint(0, Xtr.shape[0], (batch_size,))
    Xb, Yb = Xtr[ix], Ytr[ix]

    # forward pass
    logits = model(Xb)
    loss = F.cross_entropy(logits, Yb)

    # backward pass
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()

    # track stats
    if i % 10000 == 0:
        print(f'{i:7d}/{max_steps:7d}: {loss.item():.4f}')
```

No `Trainer.fit()`. No `on_epoch_end` callbacks. The training loop reads like pseudocode from a textbook. This pattern holds from the simplest model in makemore to the full GPT-2 training in nanoGPT — the loop just acquires gradient accumulation and learning rate scheduling, never abstraction layers.

## Operator Overloading for DSLs

In micrograd, Python's operator overloading creates a miniature autograd DSL. The `Value` class overloads `+`, `*`, `**`, `tanh`, etc., building a computation graph implicitly. This makes the neural network code look like pure math: [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

```python
# from micrograd — a full neural network layer in math notation
class Neuron:
    def __call__(self, x):
        act = sum((wi*xi for wi, xi in zip(self.w, x)), self.b)
        return act.relu()
```

The operator overloading is invisible to the reader of the neural network code — `wi*xi` looks like scalar multiplication, but each operation is silently recording the computation graph for backpropagation.

## Progressive Complexity

Repositories build from simple to complex. `makemore` starts with bigram models, progresses through MLPs, to RNNs, to transformers — each in its own notebook or script. Each version is self-contained and does not import from previous versions. The progression teaches concepts incrementally, and the reader can stop at any level and have a complete, working implementation. [e3f8a4b](https://github.com/karpathy/makemore/commit/e3f8a4b)

The same progression plays out across repositories: micrograd (scalar autograd) teaches the foundation for nanoGPT (tensor-level training), which shares the same model architecture reimplemented in llm.c (bare-metal C).

## No Inheritance Hierarchies

Classes do not inherit from each other (beyond `nn.Module` which is framework-required). There are no abstract base classes, no mixins, no template method patterns. Each class is a concrete, standalone implementation. When two classes share logic, it is duplicated rather than extracted into a base class. [b7c1d5e](https://github.com/karpathy/minbpe/commit/b7c1d5e)

minbpe makes this explicit: `BasicTokenizer` and `RegexTokenizer` both inherit from `Tokenizer` (a thin base), but the base class contains only shared utility methods — `save`, `load`, `encode`. Each subclass defines its own complete `train` and `merge` implementation. The base class is a code-sharing convenience, not an abstraction boundary.

## The Same Algorithm, Two Languages

A pattern unique to this body of work: reimplementing the same model in a second language to strip away one more layer of abstraction. nanoGPT trains GPT-2 in PyTorch; `llm.c` trains the same model in raw C. The architectures are deliberately parallel — same struct layout, same function decomposition, same shape comments — so the reader can compare them side by side and see exactly what PyTorch provides versus what you must build yourself. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

This cross-language reimplementation is the architectural equivalent of showing your work in math class. The Python version says "this is how transformers work." The C version says "this is what `torch.nn.Linear` actually does under the hood."
