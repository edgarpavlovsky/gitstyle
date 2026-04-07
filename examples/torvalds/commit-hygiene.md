---
title: "Commit Hygiene"
category: style
confidence: high
sources: [torvalds/linux]
related: [comments-and-docs]
last_updated: 2026-04-07
---

# Commit Hygiene

## Commit Message Format

The developer is famously particular about commit messages. The expected format:

```
subsystem: short summary (under ~72 chars)

Detailed explanation of what changed and WHY. The body can be
multiple paragraphs. Wrap at 72 characters.

Signed-off-by: Name <email>
```

The subject line uses lowercase after the subsystem prefix. No period at the end.

## Merge Commits

Merge commits from subsystem maintainers include detailed summaries of what's being merged. The developer writes custom merge messages rather than using Git's default, providing context about the pull request.

## Commit Granularity

Each commit should be a single logical change that compiles and works on its own. The developer rejects patches that mix unrelated changes, cosmetic fixes with functional changes, or incomplete work.

## Sign-off

All commits require a `Signed-off-by:` line (Developer Certificate of Origin). This is a legal and process requirement enforced across the entire project.

## Bisectability

Every commit must keep the tree in a buildable, bootable state. This is critical for `git bisect` to work. The developer has reverted commits that broke bisectability even if the final result was correct.
