---
title: Type Discipline
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
The developer demonstrates a highly language-dependent approach to type discipline, with practices varying dramatically across different programming contexts.

## Strongly Typed Languages

In [[go|Go]], the developer embraces strong typing principles. They consistently define explicit struct types for all domain models and API responses, avoiding the use of `interface{}` or generic maps [a8101e25, 88750810, 0a89c58f, 71030d80]. This disciplined approach extends to their [[c|C]] and [[cplusplus|C++]] work, where they use explicit type definitions with careful attention to integer sizes (`int8_t`, `uint32_t`, `size_t`) for memory-related operations and quantization work [e33402f7, 362c6a8d, d9862069, 5186b505, b9fb8616].

In [[rust|Rust]], the developer leverages the type system effectively, using type aliases for domain concepts (e.g., `type Pair = (u32, u32)`) and working with generics and trait bounds [7772a98a].

## Python: A Tale of Two Approaches

The developer's [[python|Python]] code reveals a striking inconsistency. Some projects demonstrate comprehensive type discipline with extensive use of type hints including complex types (`List[Dict[str, Any]]`, `Optional`, `Tuple`) and Pydantic models for API validation [eb0eb26f, 827bfd3d, 87b4a178, 6e6a5281, ebc28b95]. They also use dataclasses with type annotations for configuration objects [6694b67d, 35435ec0, 64960f99].

However, the majority of their Python code eschews type annotations entirely, relying instead on duck typing and runtime checks [9642f40b, 803f3880, 0401485f, 9fd9cc02, 633fcf2d, 419d6be2]. This suggests either evolution in their practices over time or context-dependent decisions about when type safety is worth the additional verbosity.

## Dynamic Languages

In [[javascript|JavaScript]], the developer consistently avoids type checking mechanisms. They rely on JavaScript's dynamic typing without using PropTypes, TypeScript, or even JSDoc type comments [1d8c733d, f3d83d85, 53bf4862, 6d6a4754]. The only type-related code appears to be occasional runtime `typeof` checks [46b290ea].

Similarly, in [[matlab|MATLAB]], they embrace dynamic typing with only occasional size checks for array operations [f7903a1e, d07d3fb5, a6ccad88].

## Overall Pattern

The developer appears to adopt the idiomatic type discipline of each language rather than imposing a consistent philosophy across languages. They use strong typing where the language naturally supports it (Go, Rust, C/C++) and dynamic typing where it's the norm (JavaScript, MATLAB). Their Python code represents the most interesting case, showing both extremes — possibly reflecting different project requirements or evolution in their [[language-idioms|language idiom]] preferences over time.

This pragmatic approach suggests the developer values working with language conventions rather than fighting against them, adapting their type discipline to match the ecosystem and tooling of each language.
