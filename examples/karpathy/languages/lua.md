---
title: Lua Style Guide
category: language
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
# Lua Style Guide

This developer demonstrates strong adherence to idiomatic Lua programming patterns, particularly in their use of tables and module management.

## Table-Centric Design

The developer extensively leverages Lua tables as the primary data structure for both configuration and state management, which aligns with [[language-idioms]]. In commits c24e540e, 9cb025b1, ef0373f0, and 5a1793b3, tables are consistently used to organize configuration data, plugin settings, and application state. This approach follows Lua's philosophy of "tables all the way down," where tables serve as the universal data structure for arrays, dictionaries, and objects.

## Module Organization

The codebase follows standard Lua module patterns with consistent use of `require()` for imports and proper local variable declarations (fab6fc52, 73e1715f, 6c0ef618). The developer adheres to the Lua convention of declaring module dependencies at the top of files using local variables, which improves performance by caching module references and clearly documenting dependencies.

This [[code-structure]] approach demonstrates a clear understanding of Lua's module system and its performance implications. By localizing required modules, the developer ensures faster access times and cleaner namespace management, both critical considerations in Lua development.
