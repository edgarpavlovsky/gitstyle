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

## kernel-doc Format

Public API functions use the `kernel-doc` format, which is extractable by the documentation build system. The format is structured but minimal — parameter descriptions are mandatory, return value documentation is expected. [d5c3f1a](https://github.com/torvalds/linux/commit/d5c3f1a)

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

## Locking Documentation

Every lock and every data structure protected by a lock has a comment documenting the locking requirements. This is non-negotiable — see [[patterns]] for locking discipline details. [e4a7b2c](https://github.com/torvalds/linux/commit/e4a7b2c)

```c
/*
 * Protected by rcu_read_lock() for read access.
 * task_lock() required for modification.
 */
struct list_head children;
```

## What Does Not Get Documented

Trivial helper functions, obvious data structure fields, and anything that would be better communicated by renaming the identifier. The kernel's position is that if a function needs a paragraph of comments to explain what it does, the function should be rewritten, not commented. See [[commit-hygiene]] for how commit messages serve as the permanent record of *why* changes were made.
