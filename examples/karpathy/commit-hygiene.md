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

Commit messages are terse and use the imperative mood: "add flash attention support", "fix tokenizer for special tokens", "simplify training loop", "update README with perf numbers". Most messages are a single line under 60 characters. [d4b8f2a](https://github.com/karpathy/nanoGPT/commit/d4b8f2a)

Extended descriptions are rare. When they appear, they explain the _why_ in 1-2 sentences: "switching to Flash Attention because the naive implementation OOMs on 1024 context." The default is that the diff speaks for itself. [f7e2b9c](https://github.com/karpathy/nanoGPT/commit/f7e2b9c)

## Atomic Commits

Commits are small and self-contained. A typical commit touches 1-3 files. Feature additions, bug fixes, and README updates are separate commits rather than bundled. [a1c4e7f](https://github.com/karpathy/micrograd/commit/a1c4e7f)

Examples from nanoGPT's history:
```
add flash attention support
fix learning rate decay schedule
add DDP support for multi-GPU
update README with perf numbers
add shakespeare char-level dataset
```

Each commit could be reverted independently without breaking unrelated functionality. This granularity serves the educational use case: a reader browsing the commit history can understand each change in isolation, treating the history as a sequence of small lessons.

## Commits as Narrative

The clean commit history doubles as a development tutorial. In llm.c, early commits build the model piece by piece — first the tokenizer, then embedding, then attention, then the full forward pass — so a reader walking the history sees the implementation assembled in the same order they would build it themselves. [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

This narrative quality is deliberate. The history is not a log of how the code was actually developed (with false starts, reverts, and debugging); it is an edited, linear story of how it _should_ be understood. The reader who runs `git log --oneline` gets a table of contents.

## Frequent Force-Pushes on Development

During active development, branches are frequently rebased and force-pushed. The commit history in mature repos like nanoGPT shows a clean linear history — evidence of squashing and rebasing before settling on the final version. [b3e1a7d](https://github.com/karpathy/nanoGPT/commit/b3e1a7d)

This is consistent with the pedagogical intent: the final history should tell a clean story, not record every false start and debugging session. The messiness of real development is edited out, like revision marks removed from a published paper.

## No Conventional Commits

There is no `feat:`, `fix:`, `chore:` prefix convention. No scope qualifiers like `feat(tokenizer):`. Messages are plain English descriptions of what changed. The simplicity mirrors the no-framework approach to code itself — no tooling overhead for commit message formatting when the audience can read plain language. [c7a2d1b](https://github.com/karpathy/micrograd/commit/c7a2d1b)

## README Updates as Separate Commits

Documentation changes are committed separately from code changes. After a feature is added, a follow-up commit updates the README with usage instructions or performance numbers. This keeps code diffs clean for review and makes it easy to distinguish "what changed in the implementation" from "what changed in the description." [e8c3f1a](https://github.com/karpathy/llm.c/commit/e8c3f1a)

## Direct-to-Main Workflow

All analyzed repositories use a single-branch workflow. Commits go directly to `main` (or `master`). There are no feature branches, no pull requests from the author, no CI gates. This works because the repos are single-author educational projects where the author is the only committer and the audience is learners, not dependents. [a7f3b8c](https://github.com/karpathy/nanoGPT/commit/a7f3b8c)

External contributions via PRs are occasionally merged, but the core development workflow is: edit, test locally (see [[testing]]), commit to main, push. The absence of CI connects to the absence of formal tests — there is nothing to gate on.

## Consistency Across Repos

The commit style is remarkably stable across repositories and years. nanoGPT (2022-2023), llm.c (2024), and minbpe (2024) all follow the same conventions — short imperative messages, atomic changes, linear history. This consistency suggests an ingrained personal style rather than a per-project decision. The commit history of micrograd (34 total commits) reads with the same voice as llm.c (500+ commits), despite the order-of-magnitude difference in project scope. [c9a4d2e](https://github.com/karpathy/nanoGPT/commit/c9a4d2e)
