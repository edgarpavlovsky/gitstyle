---
title: "Comments & Documentation"
category: style
confidence: high
sources: [torvalds/linux]
related: [naming-conventions, code-structure]
last_updated: 2026-04-07
---

# Comments & Documentation

## Comment Philosophy

Comments explain "why", not "what". The developer has publicly and repeatedly expressed the view that code should be readable on its own — comments that restate what the code does are considered harmful because they can become stale.

## Kernel-Doc Format

Public APIs use kernel-doc format (`/** ... */`) with parameter and return value documentation. This is extracted by the documentation build system into HTML/PDF docs.

```c
/**
 * kthread_create - create a new kernel thread
 * @threadfn: function to run in the thread
 * @data: data pointer passed to @threadfn
 * @namefmt: printf-style name for the thread
 *
 * Returns a task_struct or ERR_PTR on failure.
 */
```

## Block Comments

Multi-line comments follow the kernel style:
```c
/*
 * This is a block comment.
 * It explains a complex algorithm or non-obvious design decision.
 */
```

## Commit Messages as Documentation

The developer treats commit messages as first-class documentation. Merge commits often include detailed explanations of what a subsystem pull request contains and why. See [[commit-hygiene]] for commit message style.
