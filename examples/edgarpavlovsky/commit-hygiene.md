---
title: "Commit Hygiene"
category: style
confidence: high
sources: [edgarpavlovsky/yc-demo-day-countdown, edgarpavlovsky/token-list, edgarpavlovsky/mintlify-docs]
related: [comments-and-docs]
last_updated: 2026-04-07
---

# Commit Hygiene

## Commit Message Style

Commit messages are concise and action-oriented. The developer uses a mix of conventional commit prefixes and plain imperative-mood messages:

```
fix: handle nil countdown date
add token list validation
update docs for new API
initial commit
```

Most messages are single-line. Multi-line commit bodies are rare and used only for significant changes that need explanation.

## Commit Granularity

Commits tend to be small and focused — one logical change per commit. Large "kitchen sink" commits are uncommon. The developer appears to commit frequently, keeping each changeset reviewable.

## Branching Patterns

Based on public commit history, the developer works directly on `main` for personal projects. Feature branches appear in collaborative contexts.

## Initial Commits

New projects typically start with a substantial initial commit that includes the basic project scaffolding and a working first version, rather than starting with an empty skeleton.
