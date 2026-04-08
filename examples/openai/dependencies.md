---
title: Dependencies
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
The developer demonstrates a highly disciplined and security-conscious approach to dependency management across multiple languages and ecosystems. Their practices reveal a strong preference for stability, reproducibility, and security over convenience.

## Version Pinning and Security

The developer consistently pins dependencies to specific versions for critical packages, with a particularly notable security practice of pinning GitHub Actions to exact commit SHAs rather than version tags [cba37681] [58184ad5] [285b05d9] [be649041]. This pattern appears across multiple projects and languages, indicating a deep commitment to supply chain security.

For [[python]] projects, the developer uses multiple dependency management approaches including `pyproject.toml` with optional dependency groups [1c0ff599] [59947678], `requirements.txt` files [4bfc1f58] [e30e1418], and modern tools like `uv` for package management [45a8058f] [bec79f82]. They maintain careful version constraints, particularly for ML libraries like TensorFlow and PyTorch [8602733b] [c1a12c4c].

## Workspace-Level Management

In [[rust]] projects, the developer employs workspace-level `Cargo.toml` configurations with explicit feature flags [d90a3488] [e9702411]. They favor well-established crates from the ecosystem including tokio for async runtime, serde for serialization, and thiserror for error handling [d90a3488] [413c1e1f]. The developer actively maintains both `Cargo.lock` and `MODULE.bazel.lock` files, demonstrating careful version control across build systems.

## Abstraction and Portability

A sophisticated pattern emerges in how the developer handles optional or platform-specific dependencies. They create abstraction layers to improve portability, most notably implementing a `dist_adapter` wrapper around `torch.distributed` for cross-platform compatibility [744ed453] [be4f4cb1] [d89f2e34]. This approach extends to conditional imports for optional dependencies like MPI [9ee399f5] [b875fb7b].

The developer also migrates away from vendor-specific solutions when possible, such as replacing Google Cloud Storage dependencies with generic HTTP downloads for better portability [08efbbc1] [19533750].

## Conservative Dependency Selection

Across languages, the developer shows preference for established, well-maintained libraries over custom implementations. In [[elixir]] projects, they adopt the Phoenix framework rather than maintaining custom TCP servers [b0e0ff00]. For [[javascript]] and [[typescript]] projects, they rely on minimal dependencies, often preferring built-in Node.js modules [11a720b7] [c69527eb].

The developer actively maintains dependencies, regularly updating them for security patches while being conservative about major version changes [94c9e911] [ce90e4b3] [ded190a0]. They demonstrate awareness of deprecation cycles, proactively replacing deprecated APIs with modern alternatives [ded190a0] [dcba3cb2].

## Domain-Specific Patterns

For ML/AI projects, the developer maintains a consistent stack of scientific computing libraries (numpy, scipy, torch, tensorflow) [c26852eb] [ed2f41c4]. They handle GPU-specific dependencies with particular care, pinning exact versions of packages like flash-attn to ensure compatibility [94770399] [771ccca0].

In web projects, they integrate specialized libraries like OpenAI's agents SDK and ChatKit [3baf14ce] [43958741], while maintaining modern stacks with FastAPI for [[python]] backends and Next.js with Tailwind CSS for [[typescript]] frontends.

## Configuration-Based Dependencies

The developer uses YAML configuration files to declare external service dependencies, particularly for MCP (Model Context Protocol) server integrations [0e7823cc] [425ed2fc]. This approach separates dependency declaration from code, improving maintainability and deployment flexibility.

Their [[dockerfile]] practices reflect the same discipline, using minimal base images and installing only essential dependencies [4bfc1f58] [5b84993b], often including specific tools like wget for health checks.

Overall, the developer's dependency management style emphasizes security, reproducibility, and maintainability over rapid development, with careful attention to version compatibility and a preference for established, well-maintained libraries.
