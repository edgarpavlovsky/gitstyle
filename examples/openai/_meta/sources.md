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

- **openai-python**: Highest-signal SDK repo. Many commits are Stainless-generated; style patterns were extracted from both generated and hand-written code, noting the distinction throughout
- **openai-node**: Mirrors openai-python architecturally. Sampled to validate cross-language SDK consistency and extract TypeScript-specific idioms
- **tiktoken**: Small but high-signal for the Rust+PyO3 hybrid pattern and the `_educational.py` dual-implementation approach. Every commit is hand-written
- **whisper**: Core research archetype. Most commits from initial release; post-release commits are community fixes and model updates
- **CLIP**: Small commit count but cleanly represents research code conventions. Included to establish the research vs. SDK contrast
- **gym**: Longest-lived research repo with the most community contributions. Sampled 250 most recent and most impactful. Its interface patterns became industry-standard for RL
- **openai-cookbook**: Sampled for documentation patterns and recommended usage idioms
- **triton**: Compiler outlier — LLVM/MLIR conventions unrelated to the rest of the org. Sampled focused on Python DSL frontend and build system

## Excluded Repositories

- **openai/evals**: Evaluation framework — patterns overlap with SDK
- **openai/shap-e, point-e, consistency_models**: Small research releases, limited commit signal
- **openai/gpt-2, baselines**: Archived/legacy, not representative of current conventions

## Coverage Gaps

- **Private repositories**: Internal codebases (training infrastructure, API server, RLHF pipeline) are not public
- **Model training code**: No public repo contains production training code
- **Go/Rust services**: Likely used for backend services, but no public repos expose these

## Confidence Impact

Articles grounded in SDK code ([[patterns]], [[type-discipline]], [[naming-conventions]]) have highest confidence due to high commit volume and consistent (generated) conventions. Articles covering research code ([[testing]]) have lower confidence due to smaller samples and higher variance. Gym provides strong interface-design signal but is archived and may not reflect current direction.

**Total commits fetched:** 6,372
**Total commits sampled:** 1,252
**Unique files touched:** 3,847
**Date range:** 2016-04 to 2026-03
