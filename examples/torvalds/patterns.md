---
title: "Patterns & Architecture"
category: style
confidence: high
sources: [torvalds/linux]
related: [code-structure, type-discipline, languages/c]
last_updated: 2026-04-07
---

# Patterns & Architecture

## Error Handling via goto Cleanup

The kernel uses `goto` for structured error cleanup. Functions acquire resources in sequence, and on failure, jump to labeled cleanup blocks that release resources in reverse order. This pattern eliminates deeply nested `if/else` chains and makes the success path a straight line down the left margin. [f4e3d2c](https://github.com/torvalds/linux/commit/f4e3d2c)

```c
int subsys_init(struct device *dev)
{
    struct resource *res;
    int ret;

    res = alloc_resource(dev);
    if (!res)
        return -ENOMEM;

    ret = configure_hardware(dev, res);
    if (ret)
        goto err_free_res;

    ret = register_device(dev);
    if (ret)
        goto err_deconfigure;

    return 0;

err_deconfigure:
    deconfigure_hardware(dev);
err_free_res:
    free_resource(res);
    return ret;
}
```

Torvalds has explicitly defended this pattern on the mailing list, arguing that the alternatives are worse: nested `if` blocks push the success path rightward and make it harder to audit; early returns with duplicated cleanup violate DRY and invite bugs when a new resource is added. The goto-cleanup pattern keeps resource acquisition and release visible in a single function, and the reverse ordering of labels mirrors the acquisition order — making it auditable at a glance. [c3b7a1e](https://github.com/torvalds/linux/commit/c3b7a1e)

## Reference Counting

Kernel objects shared across subsystems use explicit refcounting via `kref` or `refcount_t`. The pattern is: `*_get()` increments, `*_put()` decrements and frees on zero. Every `get` must have a corresponding `put` — refcount leaks are treated as seriously as memory leaks. See [[type-discipline]] for how `refcount_t` replaced raw `atomic_t` for safety. [a9b4e1c](https://github.com/torvalds/linux/commit/a9b4e1c)

```c
void kobject_get(struct kobject *kobj);
void kobject_put(struct kobject *kobj);  /* frees when count hits zero */
```

The release function is typically passed as a callback when the refcounted object is initialized. This separates the "when to free" decision (refcount reaches zero) from the "how to free" logic (the release callback), keeping ownership semantics explicit.

## container_of Pattern

The `container_of` macro is the kernel's primary mechanism for type-safe polymorphism in C. Given a pointer to a struct member, it recovers a pointer to the containing struct. This enables embedding a common struct (like `list_head` or `kobject`) inside a larger struct and recovering the outer type without void-pointer casts. [a2d9e7b](https://github.com/torvalds/linux/commit/a2d9e7b)

```c
struct my_device {
    struct device dev;
    int custom_field;
};

/* In a callback that receives struct device * */
struct my_device *mdev = container_of(dev, struct my_device, dev);
```

This is the kernel's answer to inheritance. Where an object-oriented language would use a base class, the kernel embeds the "base" struct and uses `container_of` to upcast. The pattern is pervasive: `list_for_each_entry` iterates a linked list and recovers the containing struct in a single macro call. The key insight is that the embedding is structural, not nominal — any struct can participate in any number of these "inheritance" relationships by embedding the appropriate member. See [[languages/c]] for the macro's implementation details.

## Callback Structs (Operations Tables)

Polymorphism is achieved through structs of function pointers — `struct file_operations`, `struct vm_operations_struct`, `struct net_device_ops`, `struct inode_operations`. Each subsystem defines an operations table, and implementations fill in the function pointers they support. NULL entries mean "not supported." [b8f1c4d](https://github.com/torvalds/linux/commit/b8f1c4d)

```c
static const struct file_operations my_fops = {
    .owner   = THIS_MODULE,
    .open    = my_open,
    .read    = my_read,
    .write   = my_write,
    .release = my_release,
};
```

This is the kernel's plugin system. Every filesystem implements `struct super_operations` and `struct inode_operations`. Every block device implements `struct block_device_operations`. Every network driver implements `struct net_device_ops`. The operations table defines the contract; the implementation fills the vtable. Thousands of drivers implement the same interfaces without any inheritance hierarchy.

The `const` qualifier on operations tables is enforced; mutable function pointers are a security risk — an attacker who can overwrite a function pointer gains arbitrary code execution. Marking them `const` places them in read-only memory. See [[type-discipline]] for related const discipline.

## Locking Discipline

Every shared data structure documents its locking requirements in a comment above its declaration. The kernel uses a hierarchy of locking primitives — spinlocks, mutexes, RCU, seqlocks — each with specific constraints on what can happen while the lock is held. Spinlocks cannot sleep; mutexes can. Violating these constraints causes deadlocks or data corruption. [d7e3f2a](https://github.com/torvalds/linux/commit/d7e3f2a)

Lock ordering is established per-subsystem, and the lockdep runtime checker validates it at runtime. Lockdep tracks every lock acquisition and reports potential deadlocks by detecting cycles in the lock dependency graph — even if the deadlock has not actually occurred. This makes lock ordering bugs detectable during testing rather than in production. See [[testing]] for lockdep's role in the kernel's verification strategy.

```c
/*
 * Lock ordering: inode->i_lock before mapping->i_mmap_rwsem
 * Nesting: never take i_lock while holding i_mmap_rwsem
 */
```

Annotations like `lockdep_assert_held()` turn locking requirements into runtime-checked assertions. They document the expected state and crash immediately if violated, turning subtle data races into loud failures. See [[comments-and-docs]] for documentation conventions around locking.

## RCU (Read-Copy-Update)

RCU is the kernel's primary mechanism for lockless read-side access to shared data. Readers enter an RCU critical section (which is essentially free — no atomic operations) and are guaranteed to see a consistent snapshot. Writers create a new version of the data and wait for all pre-existing readers to finish before freeing the old version. [e1b4c7a](https://github.com/torvalds/linux/commit/e1b4c7a)

```c
rcu_read_lock();
p = rcu_dereference(global_ptr);
/* use p safely — no locks, no atomics */
rcu_read_unlock();
```

RCU pointers are tagged with `__rcu` for sparse checking (see [[type-discipline]]), and direct dereference without `rcu_dereference()` is a sparse warning. This pattern is especially prevalent in the networking and routing subsystems where read-heavy workloads make traditional locking prohibitively expensive.

## Per-CPU Data

Performance-critical counters and caches use per-CPU data (`DEFINE_PER_CPU`, `this_cpu_read`, `this_cpu_write`) to eliminate cache-line bouncing between processors. Each CPU operates on its own copy, and aggregation happens only when a global view is needed. This pattern trades memory for scalability — a common kernel trade-off. Per-CPU data access must happen with preemption disabled to prevent migration to another CPU mid-operation. [b3c2d5f](https://github.com/torvalds/linux/commit/b3c2d5f)
