---
title: Language Idioms
category: dimension
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
The developer demonstrates strong command of language-specific idioms across multiple programming languages, adapting their style appropriately to each language's conventions and best practices.

## Python

The developer extensively uses modern Python idioms and follows Pythonic conventions. They consistently employ list comprehensions and dictionary comprehensions for data transformations [6e85778b, 33b2b018, a83dbb21], use f-strings for string formatting [7fa0be64, 64960f99], and leverage context managers with `with` statements [7d5030b2, 6dbf2b54]. They follow standard conventions like `if __name__ == '__main__'` guards [4eb7a96b, a022d02e] and use type hints in function signatures [33b2b018, 6308e0cf].

For scientific computing, they use numpy idiomatically with broadcasting and vectorized operations rather than explicit loops [2c99eac2, f399811c]. In PyTorch code, they follow standard patterns including `nn.Module` inheritance, `super().__init__()`, and `nn.Parameter` for learnable parameters [ac30aa07, dbd4b5a1, fce68b6c]. They also use device-agnostic code with explicit device type checking for cross-platform compatibility [6104ab1b, 41af0d18, ba2554ac].

Interestingly, some older code shows Python 2.x patterns with print statements without parentheses and cPickle imports [72204877, 1a0d3051, ff7ac776], suggesting evolution in their Python usage over time.

## Go

The developer strictly follows Go idioms and conventions. They consistently return errors as the last value in function signatures, use `defer` for cleanup operations, and check errors immediately after function calls [38406bcc, 4ba1e239, 0a89c58f, a8101e25]. For database operations, they implement proper transaction handling with the `defer tx.Rollback()` pattern [4ba1e239, 9a458854] and always use SQL placeholders (?) to prevent SQL injection [38406bcc, 9a458854].

## JavaScript

The developer's JavaScript style shows evolution over time. Earlier code uses traditional patterns like constructor functions with the `new` keyword and prototype-based methods [3e62bba1, 84d69349], IIFEs for encapsulation [6d6a4754], and `for-in` loops [1d8c733d, b94827ec]. More recent code adopts modern ES6+ features including arrow functions, `const`/`let`, template literals [921f8c43, 81e4de70], and async/await patterns [eb0eb26f, 87b4a178].

They use defensive programming techniques with `typeof` checks and default parameter handling [5284e9b8, ea9d6a97], and prefer object literals for configuration patterns [f480d05e, b75b7128].

## CSS

The developer writes straightforward, vanilla CSS without preprocessors, focusing on browser compatibility [d7a303b4, 759f7e73]. They prefer explicit pixel values over relative units [759f7e73, c3cb157c], though they do use modern features like CSS custom properties for theming with semantic naming (`--ai-bg`, `--ai-border`) [ca230d95, 3cc3390f]. They follow standard property ordering and use shorthand properties appropriately [fe474d24, 419d6be2].

## CUDA/C/C++

In CUDA development, the developer demonstrates expertise with GPU-specific patterns. They use warp-level primitives, shared memory optimizations, and device-specific memory allocation strategies with fallback mechanisms [e6856bc5, e33402f7, b4623bc5]. In C code, they follow standard idioms including manual memory management with `calloc`/`malloc`, file I/O with `fread`/`fwrite`, and conditional compilation for platform-specific code [d9862069, 1fcdf04f, b9fb8616].

## Other Languages

For [[shell]] scripts, they follow Unix conventions with proper shebang lines, environment variable usage, and process management [7513852b, 111e860a]. In [[sql]], they use advanced features like CTEs (Common Table Expressions) and always parameterize queries [49a682e6, 71030d80]. Their [[lua]] code uses standard patterns like `require()` for modules and local variable declarations [fab6fc52, 73e1715f]. In [[matlab]], they leverage matrix operations idiomatically with `bsxfun` and sparse matrices for efficiency [d07d3fb5, a6ccad88].

The developer adapts their idiom usage to match each language's conventions, showing versatility and deep understanding of multiple programming paradigms.
