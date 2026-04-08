---
title: Naming Conventions
category: dimension
confidence: 0.92
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
The developer demonstrates strong consistency in naming conventions across multiple programming languages, adapting appropriately to each language's idioms while maintaining clear, descriptive names throughout their codebase.

## Language-Specific Patterns

### Python
The developer strictly follows PEP 8 naming conventions in [[python]] code. Functions and variables consistently use snake_case [ba3f3cd5, 6ed314fe, e5eabc6f], while classes use PascalCase [2d471951, f95a5fe2]. File names also follow snake_case convention [b28ddce5, b3459b11]. The developer shows a strong preference for descriptive, verbose names that clearly indicate purpose, such as `image_generation_tool_auth_allowed` [e003f84e], `resolve_workdir_base_path` [e794457a], and `_truncate_json_value_for_limit` [fb67680f].

Private methods are consistently prefixed with underscores [b1c4b6be, c373d9b9], following Python conventions for indicating internal implementation details.

### Rust
In [[rust]] code, the developer adheres strictly to Rust naming conventions with snake_case for functions, variables, and module names [e003f84e, 35b5720e, 413c1e1f], and PascalCase for types and structs [e794457a]. Examples include `build_sandbox_command` [35b5720e] and `ThreadRealtimeSdpNotification` [e794457a].

### TypeScript/JavaScript
For [[typescript]] and [[javascript]], the developer follows standard conventions with camelCase for variables and functions, PascalCase for types, interfaces, and components [8ad76b28, e67a4fc5, 6f5f0de6]. File names typically use kebab-case [d90a3488, 43958741]. Constants use SCREAMING_SNAKE_CASE [11a720b7].

### C/C++
In [[c]] and [[cplusplus]] code, the developer uses a consistent prefix pattern with `gptoss_` for public API functions and `GPTOSS_` for macros [bbc5c482, cf427a62, 9ffdd14b]. This namespace-like approach provides clear API boundaries and prevents naming conflicts.

### Other Languages
The developer adapts appropriately to other language conventions:
- [[elixir]]: snake_case for functions/variables, CamelCase for modules [ff65c7c7, 1f86bac5]
- [[shell]]: lowercase with underscores for variables [4bfc1f58, 5b84993b]
- Directory names: kebab-case for multi-word names [0e7823cc, 5c8f1e26]

## Cross-Language Patterns

Several consistent patterns emerge across languages:

1. **Descriptive Clarity**: Names clearly indicate purpose and functionality, avoiding cryptic abbreviations [35b5720e, fb67680f, 830f9b65]

2. **Action Prefixes**: Functions often start with verbs indicating their action: `test_`, `get_`, `create_`, `build_`, `resolve_` [fb67680f, 35b5720e, 45a8058f]

3. **Domain Prefixes**: Related functionality uses consistent prefixes for namespace-like organization [bbc5c482, ff65c7c7]

4. **Test Files**: Test files consistently use `test_` prefix or `_test` suffix depending on language conventions [fb67680f, ff65c7c7]

The developer's naming approach strongly emphasizes readability and self-documentation, preferring longer, more descriptive names over terse abbreviations. This pattern holds true even in performance-critical code, suggesting the developer values code clarity and maintainability.

This naming discipline extends to [[commit-hygiene]] where commit messages likely follow similar clarity principles, and supports the developer's approach to [[comments-and-docs]] by making code more self-documenting through clear naming choices.
