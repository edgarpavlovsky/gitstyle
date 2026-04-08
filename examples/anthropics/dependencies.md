---
title: Dependencies
category: dimension
confidence: 0.9
source_repos:
  - anthropics/ConstitutionalHarmlessnessPaper
  - anthropics/anthropic-cli
  - anthropics/anthropic-sdk-go
  - anthropics/anthropic-sdk-java
  - anthropics/anthropic-sdk-python
  - anthropics/anthropic-sdk-ruby
  - anthropics/anthropic-sdk-typescript
  - anthropics/anthropic-tools
  - anthropics/buffa
  - anthropics/claude-agent-sdk-demos
  - anthropics/claude-agent-sdk-python
  - anthropics/claude-agent-sdk-typescript
  - anthropics/claude-code
  - anthropics/claude-code-action
  - anthropics/claude-code-base-action
  - anthropics/claude-code-monitoring-guide
  - anthropics/claude-code-security-review
  - anthropics/claude-cookbooks
  - anthropics/claude-plugins-official
  - anthropics/claude-quickstarts
  - anthropics/claudes-c-compiler
  - anthropics/courses
  - anthropics/evals
  - anthropics/financial-services-plugins
  - anthropics/hh-rlhf
  - anthropics/knowledge-work-plugins
  - anthropics/life-sciences
  - anthropics/original_performance_takehome
  - anthropics/prompt-eng-interactive-tutorial
  - anthropics/skills
last_updated: 2026-04-08
---
The developer demonstrates a disciplined and security-conscious approach to dependency management across multiple languages and ecosystems. Their practices reveal a preference for minimal external dependencies while maintaining precise version control.

## Version Management Philosophy

The developer consistently practices strict version pinning across all package management systems. In [[python]] projects, they use `pyproject.toml` with specific version constraints [fa27d432, ca0dd33d] and maintain lock files (`uv.lock`) for reproducible builds [80b621ad, 02a4a799]. For [[javascript]] and [[typescript]] projects, they maintain synchronized updates between related packages, particularly evident in their meticulous updating of Claude Code and Agent SDK versions in lockstep [26ddc358, 39837069, e7b588b6].

A notable security practice is pinning GitHub Actions to specific commit hashes rather than version tags [0c6a49f1, 40616dd2], demonstrating awareness of supply chain security risks.

## Minimal Dependency Approach

The developer strongly favors using standard library features over external packages. In [[python]], they rely heavily on built-in modules like `copy`, `dataclasses`, `enum`, and `typing` [f88c9458, 4a79b7da]. This pattern extends to [[rust]] projects where they prefer "zero-dependency implementations" [cd002f6d, 09601e21] and [[c]] projects where they implement low-level functionality from scratch, including ELF generation and instruction encoding [e6f3fad0, e836df40].

For [[javascript]], they prefer Node.js built-in modules (using the `node:` prefix) over third-party packages [62ba73a9, df3eed3e], only adding external dependencies when truly necessary.

## Modern Tooling Choices

The developer embraces modern package managers and build tools:
- **Python**: Uses `uv` for dependency management instead of traditional pip [fa27d432, ca0dd33d]
- **JavaScript/TypeScript**: Prefers Bun over Node.js as the runtime [272de726, 7074ac04]
- **Frontend**: Consistently uses Vite for bundling, React with hooks, and Tailwind CSS [826b2685, 7e1930ff]
- **Java/Kotlin**: Uses Gradle with Kotlin DSL (`build.gradle.kts`) [52273b43, 3014518d]

## Dependency Organization

The developer maintains clear separation between different types of dependencies:
- Runtime vs. development dependencies are explicitly separated [2eb3b14a, c83ab60d]
- Optional dependencies are grouped by feature using extras in `pyproject.toml` (e.g., `[mcp]`, `[aws]`, `[vertex]`) [13e3f4bf, 4d73b215]
- In monorepo structures, they maintain separate lock files for each package [79d1d73f, 4ade5b1e]

## External Service Integration

When integrating external services, the developer prefers:
- Using official SDKs (anthropic, AWS SDK, discord.js) with explicit version pinning [00756142, 4e6907a3]
- GitHub CLI (`gh`) for GitHub operations rather than direct API calls [76826f2c, 3592c8be]
- Configuration-based integrations through JSON files over direct imports [f55b539c, fc8d9b29]

## Container and System Dependencies

In [[dockerfile]] configurations, the developer:
- Consistently uses Ubuntu 22.04 as the base image [2eb3b14a, 5a3c6f8f]
- Organizes `apt-get` installations by category with explanatory comments [2eb3b14a, 0313b3ec]
- Leverages official Docker images for monitoring components rather than custom builds [02777441]

## Automated Dependency Tracking

The developer implements sophisticated dependency tracking systems, including automated OpenAPI spec tracking with config hashes in `.stats.yml` files [90cd2008, c78eef7e], suggesting a systematic approach to managing API dependencies and versioning.
