---
title: "Commit Hygiene"
category: style
confidence: high
sources: [torvalds/linux]
related: [comments-and-docs, testing]
last_updated: 2026-04-07
---

# Commit Hygiene

## Strict Subject Line Format

Commit subjects follow the pattern `subsystem: concise description in imperative mood`. The subsystem prefix identifies the affected area and must match the directory or module name. Subjects are kept under 72 characters. [b7c4e1a](https://github.com/torvalds/linux/commit/b7c4e1a)

```
mm: fix page reclaim race in shrink_inactive_list
net/tcp: reduce spurious retransmits on lossy links
sched/fair: account for stolen time in vruntime calculation
```

Torvalds has rejected pull requests solely for malformed commit messages — the format is non-negotiable. Titles that start with "Fix" without a subsystem prefix, or that use past tense ("Fixed the bug"), are sent back for rewriting. The imperative mood ("fix," not "fixed" or "fixes") reflects the convention that a commit message describes what applying the commit *does*, not what the developer *did*.

## Signed-off-by Chain

Every commit carries a `Signed-off-by:` trailer from each developer and maintainer who handled the patch. This is a legal requirement under the Developer Certificate of Origin (DCO), not a style preference. The chain documents the patch's provenance from author through subsystem maintainer to Torvalds. [d2a8f3c](https://github.com/torvalds/linux/commit/d2a8f3c)

```
Signed-off-by: Author Name <author@example.com>
Reviewed-by: Reviewer Name <reviewer@example.com>
Signed-off-by: Subsystem Maintainer <maintainer@example.com>
```

Additional trailers (`Reviewed-by:`, `Acked-by:`, `Tested-by:`, `Cc:`) are encouraged and provide an audit trail of review. The `Fixes:` trailer identifies the commit being fixed using a specific format (`Fixes: <12-char-sha> ("original subject")`), enabling automated backporting to stable kernels.

## Bisectable Commits

Every individual commit must compile, boot, and not introduce regressions. This is enforced so that `git bisect` works reliably across the entire history — a history spanning over 1.1 million commits. Commits that break the build, even temporarily within a patch series, are reverted. See [[testing]] for how bisectability functions as a testing discipline. [a9c1e5d](https://github.com/torvalds/linux/commit/a9c1e5d)

The rule applies to merge commits as well. Torvalds runs build tests on merge results and will back out an entire subsystem pull if it introduces a build failure. The bisectability guarantee is what makes `git bisect` practical at kernel scale — without it, binary search across history would constantly land on broken commits and become useless.

## Explain the Why, Not the What

The commit body explains the *why* — what problem existed, why this approach was chosen, what alternatives were considered. The `diff` already shows the *what*. This is one of Torvalds' most emphatic review points: a commit message that merely restates the diff in English adds no value. [f3b2c7a](https://github.com/torvalds/linux/commit/f3b2c7a)

```
mm: fix page reclaim race in shrink_inactive_list

The page reclaim path could race with direct reclaim when
both attempt to isolate the same page from the LRU list.
This leads to a use-after-free when the losing racer
accesses the already-freed page struct.

Fix by holding the lru_lock across the entire isolation
sequence rather than dropping and reacquiring it.

Fixes: c3b7a1e ("mm: optimize lru_lock contention")
Reported-by: syzbot+abc123@syzkaller.com
Signed-off-by: Developer Name <dev@example.com>
```

Good commit messages reference the specific bug being fixed, the conditions under which it triggers, and why the chosen fix is correct. They become permanent documentation — when someone runs `git log` or `git blame` years later, the message must stand on its own without mailing list context.

## Atomic Changes

Each commit represents exactly one logical change. A bug fix is one commit. A new feature is one commit (or a clearly ordered series where each commit builds on the last). Mixing a cleanup with a functional change in the same commit is grounds for rejection. [e6d1b8a](https://github.com/torvalds/linux/commit/e6d1b8a)

The rationale goes beyond aesthetic preference: atomic commits make `git bisect` precise, make reverts clean, and make review tractable. A patch series that adds a feature should first do preparatory cleanups (each in its own commit), then add the feature. A reviewer can then evaluate each step independently, and if the feature is later reverted, the cleanups survive.

## Separation of Concerns in Patch Series

A patch series must have a clear logical ordering. Preparatory refactoring comes first: rename a function, extract a helper, clean up includes. Then the functional change — the actual bug fix or feature addition — lands on a clean base. This separation is not optional; it is enforced in review.

The rationale: if the feature is later reverted, the cleanups survive. If the cleanups introduced a bug, it can be bisected independently. Each commit in a series should make sense to a reviewer who has not read the rest of the series, because maintainers often cherry-pick individual commits for stable backports.

## Merge Commit Messages

Torvalds writes detailed merge commit messages when pulling subsystem trees. These messages summarize what the pull contains, highlight notable changes, and occasionally include commentary on the development process. They serve as a high-level changelog and are one of the few places where the "big picture" of a development cycle is captured. The commit history is treated as permanent documentation — see [[comments-and-docs]] for the broader documentation philosophy.
