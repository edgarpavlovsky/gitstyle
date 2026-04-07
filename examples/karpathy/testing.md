---
title: "Testing"
category: style
confidence: medium
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe]
related: [patterns, commit-hygiene]
last_updated: 2026-04-07
---

# Testing

## No Test Frameworks

None of the analyzed repositories use pytest, unittest, or any testing framework. There are no `test_*.py` files following standard conventions. Testing is manual and example-driven rather than automated and assertion-based. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

## Validation Scripts

Testing takes the form of standalone scripts that run the implementation end-to-end and print results for human inspection. `llm.c` has `test_gpt2.c` which loads a checkpoint, runs a forward pass, and prints loss values that should match the Python reference implementation. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

```c
// in test_gpt2.c
// expected loss at step 0: 5.2700
// expected loss at step 10: 4.0600
// if your loss is very different, something is wrong
```

The "test" is comparing printed output against known-good values. This is manual regression testing — effective for educational code where the user is expected to run it interactively.

## Reference Implementation Comparison

The primary testing strategy across projects is cross-validation against a reference. `llm.c` validates against PyTorch outputs. `minbpe` validates against OpenAI's tiktoken. `micrograd` validates against PyTorch autograd. The pattern is: implement from scratch, then verify outputs match the established library to within floating-point tolerance. [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

```python
# from micrograd tests — verify against PyTorch
x = Value(-4.0)
z = 2*x + 2 + x
# ... operations ...
xpt = torch.Tensor([-4.0]).double()
# ... same operations with PyTorch ...
assert abs(x.grad - xpt.grad.item()) < 1e-6
```

micrograd is the one exception that does have a `test/` directory with proper assertions, likely because gradient correctness requires numerical verification.

## Training Loss as Test Signal

For neural network code, the primary correctness indicator is training loss convergence. If loss goes down, the implementation is likely correct. README files document expected loss curves: "after 5000 iterations you should see a loss of ~1.48." [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

## Print-Based Debugging

`print()` statements are the debugging tool. Training scripts print loss, learning rate, and throughput metrics every N steps. Sample generation is interleaved with training to provide qualitative output inspection. [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

```python
if iter_num % eval_interval == 0:
    losses = estimate_loss()
    print(f"step {iter_num}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}")
if iter_num % sample_interval == 0:
    context = torch.zeros((1, 1), dtype=torch.long, device=device)
    print(decode(model.generate(context, max_new_tokens=200)[0].tolist()))
```

There is no logging framework, no structured log output, no log levels. `print()` is sufficient for code meant to be run interactively.
