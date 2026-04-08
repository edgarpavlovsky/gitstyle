---
title: Code Structure
category: dimension
confidence: 0.9
source_repos:
  - openai/CLIP
  - openai/DALL-E
  - openai/baselines
  - openai/chatgpt-retrieval-plugin
  - openai/codex
  - openai/codex-plugin-cc
  - openai/consistency_models
  - openai/evals
  - openai/gpt-2
  - openai/gpt-3
  - openai/gpt-oss
  - openai/guided-diffusion
  - openai/gym
  - openai/jukebox
  - openai/openai-agents-python
  - openai/openai-cookbook
  - openai/openai-cs-agents-demo
  - openai/openai-node
  - openai/openai-python
  - openai/openai-realtime-agents
  - openai/parameter-golf
  - openai/point-e
  - openai/shap-e
  - openai/skills
  - openai/spinningup
  - openai/swarm
  - openai/symphony
  - openai/tiktoken
  - openai/universe
  - openai/whisper
last_updated: 2026-04-08
---
The developer demonstrates a strong preference for modular code organization with clear separation of concerns across multiple programming languages and project types.

## Modular Architecture Patterns

The developer consistently creates well-defined module boundaries, organizing code into dedicated directories for different functionality types. In [[python]] projects, they separate core logic into modules like `timing.py`, `transcribe.py`, and `utils.py` [ba3f3cd5, f572f216], while maintaining clear distinctions between model implementations, utilities, and configuration [b1c4b6be, 6bc0bd88]. This pattern extends to [[rust]] projects where they extract functionality into separate crates with explicit visibility control and public re-exports at crate roots [d90a3488, 413c1e1f].

## Resource-Based Organization

A distinctive pattern emerges in the developer's approach to resource organization. They favor resource-based architectures with separate files for each API resource [b3c7207e, 0a4ca536], often implementing both sync and async versions. In [[typescript]] projects, they create nested module structures like `resources/videos/videos.ts` and `resources/responses/ws.ts` [e67a4fc5, 0064618a], while separating internal implementation details into dedicated 'internal' directories [e67a4fc5, 69125483].

## Skill-Based Directory Structures

The developer maintains highly organized skill-based directory structures with consistent patterns. Skills are organized under `.curated`, `.experimental`, and `.system` directories, with each skill containing standardized files: `SKILL.md` for documentation, `agents/openai.yaml` for metadata, `assets/` for icons, `scripts/` for utilities, and `references/` for supplementary documentation [736f600b, 14f4eb14, 0e7823cc]. This organizational pattern demonstrates exceptional consistency across multiple commits.

## Configuration Management

The developer strongly prefers centralized configuration management. They extract common values into constants and configuration objects rather than hardcoding values throughout the codebase [08efbbc1, 069d382c]. This includes creating registry patterns for hyperparameters [d3754bd3, adc9ca71] and maintaining environment variable patterns like `MONGODB_URI` and `ELASTICSEARCH_URL` [b28ddce5, b808c100].

## File Size Preferences

Interestingly, the developer shows conflicting preferences regarding file sizes. While they generally prefer small, focused functions under 20 lines [8e74fe3b, 3a8daafc], they also maintain large, monolithic files in certain contexts. [[c]] source files often exceed 1000 lines with complex functions over 100 lines [bbc5c482, cf427a62], and some [[python]] training scripts reach 1200-1800 lines [d7fbe3d1, 50390d60]. This suggests a context-dependent approach where infrastructure code remains monolithic while application code follows modular patterns.

## Cross-Platform Abstractions

The developer implements abstraction layers for cross-platform compatibility, creating adapter patterns to handle platform-specific differences [744ed453, be4f4cb1]. This is particularly evident in distributed computing utilities where they separate platform concerns into dedicated modules like `utils/dist_adapter.py` [744ed453, be4f4cb1].

## Protocol Separation

A consistent pattern emerges in how the developer separates protocol definitions from implementations. They use dedicated schema files and protocol modules [d90a3488, fb3dcfde], maintaining clear boundaries between interface definitions and their implementations. This is especially evident in [[metal]] GPU code where `.metal` shader files are kept separate from corresponding C/C++ host code [bbc5c482, 9ffdd14b].

## Build and Test Organization

The developer maintains clear separation between source code, tests, documentation, and configuration files. Tests typically mirror the source structure with comprehensive coverage for new features [fb67680f, c06cd450]. [[dockerfile]] configurations are kept minimal and single-purpose [4bfc1f58, 5b84993b], while [[cmake]] and [[makefile]] configurations follow standard conventions with clear dependency chains [b1863e83, b0e0ff00].
