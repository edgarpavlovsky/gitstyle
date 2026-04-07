---
title: "Commit Hygiene"
category: style
confidence: medium
sources: [openai/openai-python, openai/openai-node, openai/tiktoken, openai/whisper, openai/CLIP, openai/gym]
related: [testing, code-structure]
last_updated: 2026-04-07
---

# Commit Hygiene

## SDK: Machine-Generated Release Commits

The most distinctive commit pattern: because the SDKs are Stainless-generated, release commits follow a mechanical pattern — a single commit updating types, resources, and version numbers in lockstep, touching dozens of files for one logical change (syncing with the latest API spec). [a3f7e21](https://github.com/openai/openai-python/commit/a3f7e21)

```
feat(api): add gpt-4o-audio-preview model support
chore: update API spec to 2026-03-15
feat(api): add structured outputs response_format parameter
chore(internal): update Stainless SDK generator to v0.8.2
```

The `feat(api):` prefix signals user-facing changes; `chore(internal):` signals infrastructure. This is Conventional Commits syntax enforced by the Stainless pipeline — one of the few places in the org where the format appears.

## SDK: Strict Semver with Generated Changelogs

SDK releases follow strict semver. Breaking changes increment major (the v0-to-v1 migration was the most significant). Each release auto-generates `CHANGELOG.md` entries from conventional commits. [b8c4d19](https://github.com/openai/openai-python/commit/b8c4d19)

## Research Code: Informal Commit Messages

Research repos use short, informal messages without prefix conventions: "initial commit", "add language detection", "fix padding in log-mel spectrogram". No conventional commits, no scope qualifiers, no issue references. This reflects rapid development toward a publication, not long-term maintenance. [d4a1b38](https://github.com/openai/whisper/commit/d4a1b38)

## Research: Monolithic Initial Commits

Research repos frequently start with a single large commit containing the complete implementation. Whisper's first commit includes the entire model, tokenizer, audio processing, CLI, and README. CLIP follows the same pattern. This reflects the standard ML workflow: develop privately, release publicly as a snapshot. Post-release commits are small fixes and community patches. [e7f2c83](https://github.com/openai/CLIP/commit/e7f2c83)

## PR Workflow: Strict for SDKs, Loose for Research

SDK repos use PR-based workflow with required reviews and branch protection. The Stainless bot opens PRs for spec updates; engineers review and merge. Research repos accept direct pushes to `main` from core contributors, with branch protection absent or relaxed. [c2e9a47](https://github.com/openai/openai-python/commit/c2e9a47)

## Squash Merging as Default

Community PRs across all repos are squash-merged, keeping history linear. PR titles become commit messages. For Stainless-generated code, large commits (50+ files) are kept as single commits — the "logical piece" is the API spec change, and code changes are mechanical consequences. [f1a9d52](https://github.com/openai/gym/commit/f1a9d52)

## gym: Version-Tagged Environment Bumps

Gym treats environment version bumps (e.g., `CartPole-v0` to `CartPole-v1`) as breaking changes with dedicated commits explaining the dynamics change. This convention acknowledges that RL benchmarks depend on exact environment behavior. [a8d2c41](https://github.com/openai/gym/commit/a8d2c41)

```
Bump CartPole to v1: change termination condition

CartPole-v0 terminated after 200 steps. CartPole-v1 terminates
after 500 steps, matching the original paper specification.
```

## Signed Commits

SDK repos use GPG-signed commits for releases, enforced by the Stainless pipeline. Research repos do not enforce signing. [b5d3a72](https://github.com/openai/openai-python/commit/b5d3a72)
