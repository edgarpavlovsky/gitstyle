---
title: Comments and Documentation
category: dimension
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
The developer demonstrates a strong commitment to comprehensive documentation across multiple levels, from detailed README files to inline comments and function docstrings. Their documentation style varies significantly based on context and language, showing a pragmatic approach to code clarity.

## Documentation Philosophy

The developer prioritizes extensive documentation, particularly for educational and research-oriented projects. They frequently include explanatory comments that go beyond describing what code does to explain why decisions were made [e569b59f, 1076f970, 4e1694cc]. This is especially evident in their [[python]] projects where they provide comprehensive docstrings with Args and Returns sections [eb0eb26f, 827bfd3d], and in [[jupyter-notebook]] files where they heavily use markdown cells to provide educational context [ae0363ad, 36b2ad47, 882b9acc].

## README Documentation

The developer maintains exceptionally comprehensive README files that are frequently updated. These typically include:
- Detailed setup instructions and usage examples [bd8c9d87, 695de616, 0e402260]
- API documentation with code examples [88750810, 1a945f8b, a8101e25]
- Links to demos and visual examples [4c3358a3, f30ddb07, ca73a1db]
- Curated lists of community contributions and ports [350e04fe, 2eb7430e, b3c4b6c3]

They show a pattern of making frequent small updates to README files to improve user experience [bd8c9d87, 695de616, 96bbcf24], demonstrating ongoing attention to documentation quality.

## Language-Specific Patterns

The developer's commenting style varies dramatically by language:

### Verbose Languages
In [[python]], [[go]], and [[javascript]], they write extensive inline comments explaining complex logic, especially for:
- Security-critical code [38406bcc, 9a458854]
- Mathematical operations and algorithms [b4623bc5, 6e6a5281]
- Machine learning implementations [9642f40b, c6c97373]
- Academic paper references [0a20bbc1, e2fa7913, 5f49d43b]

### Minimal Documentation Languages
In [[css]], the developer consistently avoids comments, relying instead on self-documenting class names [ca230d95, 3cc3390f, eb0eb26f]. This pattern is remarkably consistent across projects [74b4fa86, 88259a07, c8a2ab52].

### Educational Content
For teaching materials, particularly in [[jupyter-notebook]] format, they provide extensive markdown documentation between code cells, including lecture descriptions, YouTube links, and learning objectives [56eda75e, 4c355970, d0ae2af9].

## Self-Critical Documentation

A distinctive trait is the developer's self-deprecating comments about code quality. They openly acknowledge hacks and express dissatisfaction with suboptimal solutions [759f7e73, c3cb157c], often soliciting improvements from others. They frequently use TODO comments to track future work [04fadeaf, ada7ef5a, ac30aa07].

## Technical Documentation

The developer creates specialized technical documentation files like CLAUDE.md for AI agents [eb0eb26f, 92e1fccb], showing awareness of different documentation audiences. They also maintain detailed development logs and instruction files [e6d79c12, c12eef77, 47ec1ade].

## Documentation Formatting

They use consistent formatting patterns:
- Visual separators (---) to highlight important information [c6de374a, 13acb58d]
- Jekyll front matter with standard metadata fields in blog posts [757d5da4, 08dc797b, 456889df]
- Structured paper notes with consistent H1 titles and bold author names [2ed34806, 5c17572e, 8e2dce39]
- Example-driven documentation with inline code snippets [4d8bc3c3, 9f43f9db]

The developer explicitly documents when code is for educational or research purposes rather than production use [46aa3d5b, aeaf0b90, a54f93cc], showing responsible documentation practices.
