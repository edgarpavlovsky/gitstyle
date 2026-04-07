---
title: "Commit Hygiene"
category: style
confidence: medium
sources: [karpathy/nanoGPT, karpathy/micrograd, karpathy/llm.c, karpathy/minbpe]
related: [testing, code-structure]
last_updated: 2026-04-07
---

# Commit Hygiene

## Short, Imperative Messages

Commit messages are terse and use the imperative mood: "add flash attention support", "fix tokenizer for special tokens", "simplify training loop", "update README". Most messages are a single line under 60 characters. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

Extended descriptions are rare. When they appear, they explain the _why_ in 1-2 sentences: "switching to Flash Attention because the naive implementation OOMs on 1024 context." [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

## Atomic Commits

Commits are small and self-contained. A typical commit touches 1-3 files. Feature additions, bug fixes, and README updates are separate commits rather than bundled. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

Examples from nanoGPT:
```
add flash attention support
fix learning rate decay schedule
add DDP support for multi-GPU
update README with perf numbers
add shakespeare char-level dataset
```

Each commit could be reverted independently without breaking unrelated functionality.

## Frequent Force-Pushes on Development

During active development, branches are frequently rebased and force-pushed. The commit history in mature repos like nanoGPT shows a clean linear history — evidence of squashing and rebasing before settling on the final version. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

This is consistent with educational code: the final history should tell a clean story, not record every false start and debugging session.

## No Conventional Commits

There is no `feat:`, `fix:`, `chore:` prefix convention. No scope qualifiers like `feat(tokenizer):`. Messages are plain English descriptions of what changed. The simplicity mirrors the no-framework approach to code itself. [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

## README Updates as Separate Commits

Documentation changes are committed separately from code changes. After a feature is added, a follow-up commit updates the README with usage instructions or performance numbers. This keeps code diffs clean for review. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

## Direct-to-Main Workflow

All analyzed repositories use a single-branch workflow. Commits go directly to `main` (or `master`). There are no feature branches, no pull requests from the author, no CI gates. This works because the repos are single-author educational projects, not collaborative production code. [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

External contributions via PRs are occasionally merged, but the core development workflow is: edit, test locally, commit to main, push.
