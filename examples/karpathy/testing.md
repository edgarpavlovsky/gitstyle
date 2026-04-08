---
title: Testing
category: dimension
confidence: 0.85
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
The developer exhibits highly varied testing practices across different projects and languages, ranging from comprehensive test suites to complete absence of automated testing.

## Language-Specific Patterns

### Go: Comprehensive Table-Driven Testing

In [[go]] projects, the developer demonstrates sophisticated testing practices. They consistently write comprehensive table-driven tests with helper functions for test setup [38406bcc, eed8b1b9, 9a458854]. Test helpers like `newTestApp()` and `markdownHTML()` reduce boilerplate and improve readability [38406bcc, eed8b1b9, 9a458854, 0a89c58f, a8101e25]. Tests cover both happy paths and edge cases, including security scenarios like self-engagement gaming [eed8b1b9, 49a682e6, 38406bcc]. The developer focuses on behavior and integration testing rather than isolated unit tests [38406bcc, eed8b1b9, 0a89c58f].

### Python: Mixed Approaches

In [[python]] projects, the developer's testing approach varies significantly:

- **With pytest**: When using established frameworks, they create comprehensive test suites with parameterized tests [d278867d, 45cb371b, e82c123c, 37b63c28]
- **PyTorch validation**: Adds comprehensive unit tests comparing against PyTorch for correctness validation [315a2cb3, 5973e7b3, 315dda3d]
- **Runtime validation**: Often includes runtime validation and fast-fail checks rather than formal tests [c2450add, 0be1e4fd]
- **No testing**: Many Python projects lack any test files or testing infrastructure [eb0eb26f, 827bfd3d, 87b4a178, 8affe1d7, 92e1fccb]

### Low-Level Languages: Gradient Testing

For [[c]], [[cplusplus]], and [[cuda]] projects, the developer maintains dedicated test files (e.g., `test_gpt2.cu`) with gradient checking and validation against expected outputs [f1e2ace6, e33402f7]. This shows commitment to numerical correctness verification in performance-critical code.

### JavaScript: Demo-Based Testing

In [[javascript]] projects, the developer rarely uses formal testing frameworks. One exception shows Jasmine framework adoption with gradient checking tests [f1addd3a]. More commonly, they rely on:
- Interactive web demos for validation [80e61f4c, 0b9315a6, 32706e14, 08af2a2f]
- Demo HTML files for manual testing [3e62bba1, 32ea5fc6, 3ba9014c]
- Simple assertion-based tests in Node.js [f480d05e]

## Testing Philosophy

The developer appears to follow a "vibe coding" approach in many projects [64960f99], prioritizing rapid prototyping over test-driven development. They often rely on:

- **Manual testing**: Through demo scripts, dry-run flags, and debugging options [48a7e01a, 23b0e109]
- **Evaluation scripts**: Rather than unit tests, especially in ML projects [2c99eac2, 83366151, 63607a7e]
- **Interactive notebooks**: For validation in [[jupyter-notebook]] projects [ae0363ad, 36b2ad47, 333e0441]
- **Production monitoring**: Bug fixes appear reactive to user reports rather than proactive testing [2d62a1c4, 13ece5d7]

## Cross-Language Patterns

The developer shows interesting cross-language testing patterns:
- Writes Python-based integration tests for [[rust]] code, including property-based testing and benchmarks [1eb8e821, 7772a98a]
- Maintains test coverage when making architectural changes [1076f970]
- Documents performance impacts in [[commit-hygiene]] through experimental validation [6ed7d1d8, 4b407742, 4e1694cc]

## Notable Exceptions

Some projects stand out for their testing approach:
- Bitcoin-related Python code includes comprehensive unit tests mirroring main code structure [7cf9c084, a3906161, 48a07a07]
- [[lua]] projects include test functions and cross-validation utilities [73e1715f, 7513852b]
- [[matlab]] projects use demo scripts for functionality testing [f7903a1e, d07d3fb5, 0e6fb20c]

The developer's testing practices strongly correlate with project maturity and language ecosystem, showing adaptability but also a general preference for manual validation over automated testing in experimental or prototype code.
