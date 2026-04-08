---
title: C++ Style Guide
category: language
confidence: 0.9
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
The developer demonstrates proficiency with modern C++ in the context of CUDA programming, showing careful attention to memory management and error handling patterns.

## CUDA-Specific C++ Patterns

The codebase reveals sophisticated use of [[cuda]] programming patterns within C++. The developer implements robust device memory management with intelligent fallback strategies (e6856bc5), utilizing CUDA's unified memory when available and falling back to explicit memory transfers when necessary. This shows a pragmatic approach to [[code-structure]] that prioritizes compatibility across different CUDA architectures.

Warp-level primitives are employed effectively (e33402f7), indicating deep understanding of GPU programming [[patterns]]. The code leverages these low-level optimizations while maintaining readability through well-structured abstractions.

## Error Handling and Macros

A consistent pattern emerges in error checking through custom macros (8c586f91). Rather than raw CUDA API calls, the developer wraps operations in error-checking macros that provide meaningful diagnostics. This approach to [[language-idioms]] balances performance with debuggability, a critical consideration in GPU programming where errors can be difficult to trace.

The macro usage extends beyond simple error checking, suggesting a preference for compile-time configuration and conditional compilation strategies typical of systems-level C++ development.
