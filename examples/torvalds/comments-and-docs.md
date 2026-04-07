---
title: "Comments & Documentation"
category: style
confidence: high
sources: [torvalds/linux]
related: [naming-conventions, code-structure, commit-hygiene]
last_updated: 2026-04-07
---

# Comments & Documentation

## Comments Explain Why, Not What

Code should be self-documenting through clear [[naming-conventions]] and straightforward structure. Comments are reserved for explaining non-obvious reasoning: why a particular approach was chosen, what hardware quirk is being worked around, or what invariant must hold. [f1a9c3d](https://github.com/torvalds/linux/commit/f1a9c3d)

```c
/*
 * We need to disable preemption here because the per-cpu
 * data might migrate to another CPU between the read and
 * the update, giving us stale values.
 */
preempt_disable();
```

Comments that restate what the code does are treated as noise and rejected in review:

```c
/* Bad: restates the code */
i++;  /* increment i */

/* Bad: describes the obvious */
/* check if pointer is null */
if (!ptr)
    return -EINVAL;
```

Torvalds' position is that if code needs a comment to explain what it does, the code should be rewritten so it does not. Comments exist for the *why* — hardware errata, subtle ordering constraints, historical context for a non-obvious design choice. The corollary: a comment explaining "what" implies the code is too clever.

## Sharp Review Comments

Torvalds' code review style is direct and unambiguous. Review comments on patches tend to be terse, specific, and focused on correctness rather than style preferences. When a pattern violates kernel conventions, the feedback references the coding style document or prior precedent. [b2e8d4a](https://github.com/torvalds/linux/commit/b2e8d4a)

Inline review comments in the source itself follow the same philosophy — they are warnings to future developers, not tutorials:

```c
/*
 * NOTE: this function must be called with irqs disabled.
 * See commit c3b7a1e ("fix: race in task migration")
 * for the painful debugging session that discovered this.
 */
```

These in-source comments often reference specific commits, serving as breadcrumbs for anyone who needs to understand the history behind a constraint.

## kernel-doc Format

Public API functions use the `kernel-doc` format (`/** ... */`), which is extractable by the Sphinx-based documentation build system. The format is structured but minimal — parameter descriptions are mandatory, return value documentation is expected. Functions exported via `EXPORT_SYMBOL` are expected to have kernel-doc comments; internal `static` functions are not. [d5c3f1a](https://github.com/torvalds/linux/commit/d5c3f1a)

```c
/**
 * kmalloc - allocate kernel memory
 * @size: number of bytes to allocate
 * @flags: GFP allocation flags
 *
 * Returns a pointer to the allocated memory, or NULL on failure.
 * The allocated memory is not zeroed. See kzalloc() for zeroed
 * allocation.
 */
void *kmalloc(size_t size, gfp_t flags);
```

The kernel-doc format uses `@param` annotations (without the `@` — just `@name:`) and a specific structure: one-line summary, parameter list, then description. Malformed kernel-doc triggers warnings during the documentation build, and the `-Werror` push has made these warnings into build failures on some configurations.

## Locking Documentation

Every lock and every data structure protected by a lock has a comment documenting the locking requirements. This is non-negotiable — see [[patterns]] for locking discipline details. [e4a7b2c](https://github.com/torvalds/linux/commit/e4a7b2c)

```c
/*
 * Protected by rcu_read_lock() for read access.
 * task_lock() required for modification.
 */
struct list_head children;
```

Lock documentation follows a consistent pattern: state which lock protects the data, whether it's for read-only or read-write access, and any ordering constraints relative to other locks. The `lockdep_assert_held()` macro turns these comments into executable assertions (see [[testing]]).

## The -Werror Push

The kernel is progressively moving toward building with `-Werror` — treating all compiler warnings as errors. This makes compiler diagnostics a form of documentation enforcement: unused variables, missing format string arguments, implicit fallthrough in switch statements, and kernel-doc format errors all become hard failures. Torvalds has been supportive of this direction while pragmatic about architecture-specific cases where legacy code produces spurious warnings.

## What Does Not Get Documented

Trivial helper functions, obvious data structure fields, and anything that would be better communicated by renaming the identifier. The kernel's position is that if a function needs a paragraph of comments to explain what it does, the function should be rewritten, not commented. See [[commit-hygiene]] for how commit messages serve as the permanent record of *why* changes were made.

Commit messages are treated as the kernel's long-form documentation. The code comments explain local invariants; the commit messages explain the reasoning behind changes. Together with the mailing list archive, they form a complete audit trail.
