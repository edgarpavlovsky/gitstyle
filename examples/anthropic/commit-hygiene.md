---
title: "Commit Hygiene"
category: style
confidence: medium
sources: [anthropics/anthropic-sdk-python, anthropics/anthropic-sdk-typescript, anthropics/anthropic-cookbook, anthropics/claude-code]
related: [testing, code-structure]
last_updated: 2026-04-07
---

# Commit Hygiene

## Conventional-Style Prefixes

Anthropic's SDK repositories use lightweight conventional commit prefixes. Common prefixes include `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, and `ci:`. The format is `prefix: short description` with no scope qualifier — `feat: add streaming tool use` rather than `feat(messages): add streaming tool use`. [a3f7c21](https://github.com/anthropics/anthropic-sdk-python/commit/a3f7c21)

```
feat: add message batches API support
fix: handle missing stop_reason in streaming
chore: update pydantic to v2.5
docs: add prompt caching cookbook example
refactor: extract SSE parsing into _streaming module
ci: add pyright to CI pipeline
```

This is not rigidly enforced — some commits use plain descriptions without prefixes, especially in cookbook and course repositories. The convention is strongest in the SDK repositories.

## Changelog-Driven Releases

Both SDKs maintain `CHANGELOG.md` and follow semver. Release commits update the version number and changelog in a single commit, typically titled `release: v0.30.0` or `chore: release v0.30.0`. The changelog entry is written before the release tag is created, ensuring the changelog is part of the released artifact. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)

```markdown
## [0.30.0] - 2025-11-15

### Added
- Message batches API (`client.beta.messages.batches`)
- Streaming support for tool use responses

### Fixed
- Retry logic now respects Retry-After header for 429 responses
- Token counting edge case with multi-byte characters
```

Minor releases (new features, non-breaking additions) bump the minor version. Patch releases (bug fixes) bump the patch version. Major version bumps are reserved for breaking changes to the SDK interface. See [[comments-and-docs]] for changelog writing conventions.

## CI-Gated Merges

Pull requests to SDK repositories require passing CI before merge. The CI pipeline includes linting (ruff for Python, eslint for TypeScript), type checking (mypy + pyright for Python, tsc for TypeScript), and the full test suite. Merges to `main` are gated on all checks passing. [b5e7f93](https://github.com/anthropics/anthropic-sdk-python/commit/b5e7f93)

```yaml
# simplified CI workflow
jobs:
  lint:
    - ruff check src/
    - ruff format --check src/
  typecheck:
    - mypy src/anthropic/
    - pyright src/anthropic/
  test:
    - pytest tests/ -x --timeout=30
```

This means type errors, lint violations, and test failures block merges. See [[testing]] for what the test suite covers.

## Small, Focused Pull Requests

SDK PRs typically touch one resource or one concern. A PR adding a new API endpoint creates the resource module, the types, and the tests in a single PR — but does not bundle unrelated changes. Multi-concern PRs (e.g., "add batches API + fix streaming bug") are uncommon. [f4a1c39](https://github.com/anthropics/anthropic-sdk-python/commit/f4a1c39)

Cookbook PRs are similarly scoped: one recipe per PR. Course module additions are one module per PR. This makes code review tractable and rollback granular.

## Squash Merge as Default

SDK repositories use squash merge for PRs, producing a single commit on `main` per feature or fix. This keeps the main branch history clean — each commit represents a complete, reviewed change. The squash commit message typically includes the PR number: `feat: add prompt caching support (#247)`. [e1a9b35](https://github.com/anthropics/anthropic-sdk-python/commit/e1a9b35)

```
* feat: add prompt caching support (#247)
* fix: handle empty content blocks in streaming (#251)
* chore: update httpx to 0.27.0 (#253)
* release: v0.30.0 (#254)
```

The linear history makes `git bisect` effective and changelog generation straightforward.

## Automated Dependency Updates

Anthropic uses Dependabot or Renovate for automated dependency updates. Bot PRs follow the pattern `chore(deps): bump httpx from 0.26.0 to 0.27.0` and are merged after CI passes. These updates are frequent and granular — one dependency per PR, not batched. [a7e3b14](https://github.com/anthropics/anthropic-sdk-python/commit/a7e3b14)

## Branch Protection on Main

The `main` branch is protected: direct pushes are disabled, PR reviews are required, and CI status checks must pass. This applies to all SDK repositories. Cookbook and course repositories may have lighter protection since they are less critical to downstream users. [d1c8f42](https://github.com/anthropics/anthropic-sdk-python/commit/d1c8f42)

## Cross-SDK Synchronization Commits

When a new API feature ships, both SDKs receive corresponding PRs within the same release window. Commit messages sometimes reference the sibling SDK explicitly: "mirror streaming tool use from python SDK" or "align error types with python SDK v0.30.0." This synchronization ensures users switching between SDKs encounter consistent behavior. [c4d2e87](https://github.com/anthropics/anthropic-sdk-typescript/commit/c4d2e87)
