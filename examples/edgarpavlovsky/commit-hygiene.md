---
title: "Commit Hygiene"
category: style
confidence: high
sources: [edgarpavlovsky/pulse-ios, edgarpavlovsky/token-list, edgarpavlovsky/shipkit, edgarpavlovsky/yc-demo-day-countdown, edgarpavlovsky/gitstyle]
related: [comments-and-docs, code-structure, dependencies]
last_updated: 2026-04-07
---

# Commit Hygiene

## Conventional Commit Messages

The developer uses conventional commit prefixes consistently across all repositories. The format is `type: short description` in lowercase, with no trailing period. [a9e1b0c](https://github.com/edgarpavlovsky/shipkit/commit/a9e1b0c)

Observed prefixes and their frequency:
- `feat:` — new features and capabilities (~40% of commits)
- `fix:` — bug fixes (~25%)
- `refactor:` — code restructuring without behavior change (~15%)
- `chore:` — dependency updates, CI config, tooling (~12%)
- `docs:` — README and doc comment updates (~5%)
- `test:` — adding or fixing tests (~3%)

```
feat: add token search with fuzzy matching
fix: handle nil countdown date on first launch
refactor: extract network layer into dedicated service
chore: update SPM dependencies
docs: add API usage example to README
test: add snapshot tests for onboarding flow
```

## Atomic Commits

Each commit contains exactly one logical change. The developer does not batch unrelated changes into a single commit, even small ones. A characteristic example: a PR that added a new feature had 4 commits — one for the model, one for the service, one for the view, and one for the tests. [3da7f12](https://github.com/edgarpavlovsky/pulse-ios/commit/3da7f12)

This makes `git bisect` and `git revert` practical, which aligns with a general preference for maintainable history over minimal commit count.

## Feature Branch Workflow

All work happens on feature branches named `type/short-description`:
- `feat/token-search`
- `fix/countdown-nil-crash`
- `refactor/networking-layer`

Branches are merged via squash merge on GitHub, keeping the main branch history clean. The developer does not rebase interactively to craft a perfect history — instead, small atomic commits on the branch and a squash merge handle this naturally. [71bc9e3](https://github.com/edgarpavlovsky/token-list/commit/71bc9e3)

## Separation of Concerns in Commits

The developer separates different types of changes into distinct commits, even when done as part of the same work:

1. Dependency updates get their own commit (see [[dependencies]])
2. Refactors that enable a feature are committed before the feature itself
3. Code formatting or linting changes are never mixed with logic changes
4. Documentation updates are separate from code changes (see [[comments-and-docs]])

A PR introducing a new payment flow shows this discipline: `refactor: extract base subscription service` followed by `feat: add annual subscription option`. [8c2d4f1](https://github.com/edgarpavlovsky/pulse-ios/commit/8c2d4f1)

## No WIP Commits on Main

The main branch never contains work-in-progress commits. Every commit on main is a complete, working unit. WIP commits may exist on feature branches but are squashed away before merging. [d42ea91](https://github.com/edgarpavlovsky/shipkit/commit/d42ea91)
