---
title: "Data Sources"
category: meta
last_updated: 2026-04-07
---

# Data Sources

## Repositories Analyzed

| Repository | Commits Fetched | Commits Sampled | Primary Language | Category |
|------------|----------------|-----------------|------------------|----------|
| openai/openai-python | 487 | 210 | Python | SDK |
| openai/openai-node | 412 | 185 | TypeScript | SDK |
| openai/tiktoken | 89 | 78 | Python + Rust | Tooling |
| openai/whisper | 74 | 68 | Python | Research |
| openai/CLIP | 31 | 31 | Python | Research |
| openai/gym | 1,842 | 250 | Python | Research |
| openai/openai-cookbook | 623 | 180 | Python (Jupyter) | Documentation |
| openai/triton | 2,814 | 250 | Python + C++ | Compiler |

## Sampling Notes

- **openai-python**: Highest-signal repo for SDK conventions. Many commits are Stainless-generated — style patterns were extracted from both generated and hand-written code, noting the distinction
- **openai-node**: Mirrors openai-python architecturally. Sampled to validate cross-language SDK consistency and extract TypeScript-specific idioms
- **tiktoken**: Small but high-signal for the Rust+Python hybrid pattern. Every commit is hand-written
- **whisper**: Core research repo. Most commits are from the initial release; post-release commits are community fixes and model updates
- **CLIP**: Small commit count but represents the "research code" archetype clearly. Included to establish the research vs. SDK contrast
- **gym**: Largest commit history among research repos due to its long active lifespan and community contributions. Sampled 250 most recent and most impactful
- **openai-cookbook**: Sampled for documentation patterns and recommended usage idioms. Not a code library but shapes how the org communicates patterns
- **triton**: Very large commit history. Sampled focused on Python DSL frontend and build system, not deep MLIR internals

## Excluded Repositories

- **openai/evals**: Evaluation framework — patterns overlap with SDK, less distinctive
- **openai/shap-e**: Small research release, limited commit signal
- **openai/point-e**: Small research release, similar to CLIP in structure
- **openai/consistency_models**: Research release with minimal post-publication activity
- **openai/gpt-2**: Archived/legacy, does not represent current conventions
- **openai/baselines**: Archived RL code, superseded by gym patterns

## Coverage Gaps

- **Private repositories**: OpenAI's internal codebases (GPT training infrastructure, API server, RLHF pipeline) are not on GitHub — only public repositories are analyzed
- **Model training code**: No public repository contains production model training code; whisper and CLIP represent research training only
- **Infrastructure code**: Deployment, scaling, and serving code is private
- **Go/Rust services**: OpenAI likely uses Go and Rust for backend services, but no public repos expose these patterns

## Confidence Impact

Articles grounded in SDK code (e.g., [[patterns]], [[type-discipline]], [[naming-conventions]]) have the highest confidence due to high commit volume and consistent conventions. Articles extrapolating from research code (e.g., [[testing]] for research repos) have lower confidence due to smaller sample size and higher variance between repos. The [[commit-hygiene]] article bridges both categories and notes where conventions diverge.

The gym repository provides strong signal for interface design patterns but represents a mature/archived project — its conventions may not reflect current organizational direction.

**Total commits fetched:** 6,372
**Total commits sampled:** 1,252
**Unique files touched:** 3,847
**Date range:** 2016-04 to 2026-03
