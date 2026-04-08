---
title: Shell Style Guide
category: language
confidence: 0.82
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
The developer demonstrates proficiency in shell scripting with consistent adherence to Unix conventions and modern best practices.

## Script Structure and Initialization

The developer follows standard Unix [[patterns]] for shell scripts, consistently using proper shebang lines and environment setup. In commit 7513852b, scripts begin with `#!/bin/bash` and immediately establish the execution environment with exports like `LANG=en_US.UTF-8` and `LC_ALL=en_US.UTF-8`, demonstrating attention to locale handling (65cf485b).

## Environment and Configuration Management

A strong pattern emerges in the developer's approach to configuration through environment variables. Scripts extensively use environment variable checks and conditional logic (111e860a, 2d7f1ba4, 947478d1). In commits ff463007, c16db281, and 685271dc, the developer shows preference for environment-based configuration over hardcoded values, following Unix [[language-idioms]] of making scripts configurable and portable.

## Process and Session Management

The developer demonstrates competence with Unix process management tools. In commit 7513852b, proper use of GNU screen for session management is evident, showing understanding of long-running process handling in shell environments. Scripts include robust process management patterns (74b4fa86), with careful attention to background processes and session persistence.

## Cross-Platform Considerations

While primarily focused on Unix-like systems, the developer shows awareness of platform differences. Commits cb445113 and 29aacba1 reveal consideration for cross-platform compatibility, though these appear to be in other languages that the shell scripts might interact with.

## Error Handling and Robustness

The developer implements defensive programming practices in shell scripts, with conditional checks before operations (947478d1) and proper handling of edge cases. The consistent use of environment variable validation demonstrates a focus on script reliability.

## Integration with Other Languages

The developer's shell scripts often serve as orchestration layers for polyglot projects. Evidence from eb0eb26f shows shell scripts managing [[python]] environments with proper package structures, and integration with [[javascript]] React applications, demonstrating the developer's use of shell as a glue language in modern development workflows.
