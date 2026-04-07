---
title: "Naming Conventions"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, comments-and-docs, languages/c]
last_updated: 2026-04-07
---

# Naming Conventions

## snake_case Everything

All identifiers use `snake_case` without exception. CamelCase is explicitly rejected in code review — the kernel coding style document reflects this, and Torvalds enforces it aggressively in merge reviews. [b3a7f1d](https://github.com/torvalds/linux/commit/b3a7f1d)

```c
/* Correct */
struct task_struct *find_task_by_pid(pid_t pid);
int nr_running;
void schedule_timeout(long timeout);

/* Rejected in review */
struct TaskStruct *FindTaskByPid(pid_t pid);  /* never */
```

## Short Locals, Descriptive Globals

Local variables are kept short — single letters for loop counters, brief abbreviations for function-scoped temporaries. Global and file-scope symbols get descriptive names because they need to be greppable across millions of lines. [d8e2c4a](https://github.com/torvalds/linux/commit/d8e2c4a)

```c
/* Typical local naming */
int i, ret;
struct page *p;
unsigned long flags;

/* Typical global naming */
unsigned long total_forks;
struct rw_semaphore namespace_sem;
```

The variable `ret` deserves special mention: it is the universal name for a function's return value, used in virtually every non-trivial kernel function. Seeing `ret` in kernel code immediately communicates "this is the error code that will be returned."

## Subsystem-Prefixed Functions

Public functions are prefixed with their subsystem name to create a namespace in C's flat symbol space. The prefix acts as a module boundary indicator — see [[code-structure]] for how this maps to directory layout.

```c
/* VFS subsystem */
int vfs_open(const struct path *path, struct file *file);
int vfs_read(struct file *file, char __user *buf, size_t count, loff_t *pos);

/* Memory management */
struct page *alloc_pages(gfp_t gfp_mask, unsigned int order);
void __free_pages(struct page *page, unsigned int order);

/* Networking */
int tcp_v4_connect(struct sock *sk, struct sockaddr *uaddr, int addr_len);
void tcp_send_ack(struct sock *sk);
```

The double-underscore prefix (`__free_pages`) denotes an internal variant that skips some validation — a convention used consistently across subsystems. This creates a two-level API: the public function validates inputs and calls the `__` variant for the actual work. [a5f9b2e](https://github.com/torvalds/linux/commit/a5f9b2e)

## Struct Naming

Structs are named descriptively and never typedef'd (see [[type-discipline]]). The `struct` keyword is always spelled out. Struct member names are kept short since they're always qualified by the struct variable:

```c
struct vm_area_struct {
    unsigned long vm_start;
    unsigned long vm_end;
    struct mm_struct *vm_mm;
    pgprot_t vm_page_prot;
};
```

The `vm_` prefix on members mirrors the struct's role — this per-subsystem member prefix is a consistent kernel convention. It prevents name collisions when macros or generic code operates on member names, and it makes grepping for all uses of a particular field reliable.

## Macro Naming

Macros use `UPPER_SNAKE_CASE`. Function-like macros that evaluate arguments multiple times are generally avoided in favor of `static inline` functions, but when macros are necessary, the naming makes their macro nature visible. See [[languages/c]] for macro idiom details. [e1c7d3f](https://github.com/torvalds/linux/commit/e1c7d3f)

## Abbreviation Conventions

The kernel has a stable vocabulary of abbreviations used across all subsystems: `nr` (number), `prev`/`next`, `src`/`dst`, `len`, `buf`, `ctx` (context), `ops` (operations), `cb` (callback), `priv` (private data), `desc` (descriptor). These are used consistently enough that they function as domain-specific shorthand — a new kernel developer learns them once and reads them everywhere.

## Error Constants

Error returns use the standard negative `errno` values (`-ENOMEM`, `-EINVAL`, `-ENOSPC`). Functions that can fail return `int` with zero for success and a negative errno on failure. Pointer-returning functions use `ERR_PTR()` / `IS_ERR()` / `PTR_ERR()` to encode errors in the pointer value, avoiding the need for a separate output parameter. This convention is so pervasive that violating it — returning `NULL` where `ERR_PTR(-ENOMEM)` is expected — is a common source of bugs caught in review. [c4d8f2a](https://github.com/torvalds/linux/commit/c4d8f2a)
